#!/usr/bin/env bash
# =============================================================================
# Post-deployment script: Configure PostgreSQL roles in Docker containers
#
# This script connects to each service instance via SSH (through the gateway)
# and configures the admin and CRUD roles in the PostgreSQL containers.
#
# Prerequisites:
#   - CDK infrastructure deployed
#   - Docker Compose running on each instance (with postgres container)
#   - SSH access configured (ssh-add your key first)
#
# Usage:
#   ./setup-db-roles.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# Load .env
ENV_FILE="${SCRIPT_DIR}/.env"
if [ ! -f "$ENV_FILE" ]; then
  error ".env file not found at ${ENV_FILE}"
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

# Validate required variables
REQUIRED_VARS=(DB_ADMIN_USERNAME DB_ADMIN_PASSWORD DB_CRUD_USERNAME DB_CRUD_PASSWORD)
for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var:-}" ]; then
    error "Required variable ${var} is not set in .env"
    exit 1
  fi
done

# --- Configuration ---
REGION="${CDK_DEFAULT_REGION:-eu-north-1}"
GATEWAY_USER="admin"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

# Service definitions: name, database name, private IP env var
SERVICES=(
  "gateway:cmv_gateway"
  "patients:cmv_patients"
  "chambres:cmv_chambres"
)

# --- Resolve IPs from CloudFormation outputs ---
info "Fetching instance IPs from CloudFormation outputs..."

GATEWAY_PUBLIC_IP=$(aws cloudformation describe-stacks \
  --stack-name CmvInfrastructureStack \
  --query "Stacks[0].Outputs[?ExportName=='CmvGatewayPublicIp'].OutputValue" \
  --output text --region "$REGION" 2>/dev/null || echo "")

if [ -z "$GATEWAY_PUBLIC_IP" ]; then
  error "Could not resolve gateway public IP from CloudFormation outputs."
  error "Make sure the CDK stack is deployed."
  exit 1
fi

info "Gateway public IP: ${GATEWAY_PUBLIC_IP}"

# Fetch private IPs for each service
declare -A SERVICE_IPS
for svc_entry in "${SERVICES[@]}"; do
  svc_name="${svc_entry%%:*}"
  capitalized="$(echo "${svc_name:0:1}" | tr '[:lower:]' '[:upper:]')${svc_name:1}"
  
  ip=$(aws cloudformation describe-stacks \
    --stack-name CmvInfrastructureStack \
    --query "Stacks[0].Outputs[?ExportName=='Cmv${capitalized}PrivateIp'].OutputValue" \
    --output text --region "$REGION" 2>/dev/null || echo "")
  
  if [ -z "$ip" ]; then
    warn "Could not resolve private IP for ${svc_name}, skipping."
    continue
  fi
  
  SERVICE_IPS["$svc_name"]="$ip"
  info "${svc_name} private IP: ${ip}"
done

# --- Configure roles on each service ---
configure_db_roles() {
  local svc_name="$1"
  local db_name="$2"
  local target_ip="$3"

  info "Configuring PostgreSQL roles on ${svc_name} (${target_ip})..."

  # Build the SQL commands
  local sql_commands
  sql_commands=$(cat << SQLEOF
-- Create database if not exists
SELECT 'CREATE DATABASE ${db_name}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${db_name}')\\gexec

-- Create admin role
DO \\\$\\\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_ADMIN_USERNAME}') THEN
    CREATE USER ${DB_ADMIN_USERNAME} WITH PASSWORD '${DB_ADMIN_PASSWORD}';
  ELSE
    ALTER USER ${DB_ADMIN_USERNAME} WITH PASSWORD '${DB_ADMIN_PASSWORD}';
  END IF;
END
\\\$\\\$;

-- Grant admin full privileges
ALTER USER ${DB_ADMIN_USERNAME} CREATEDB CREATEROLE SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE ${db_name} TO ${DB_ADMIN_USERNAME};

-- Create CRUD role
DO \\\$\\\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_CRUD_USERNAME}') THEN
    CREATE USER ${DB_CRUD_USERNAME} WITH PASSWORD '${DB_CRUD_PASSWORD}';
  ELSE
    ALTER USER ${DB_CRUD_USERNAME} WITH PASSWORD '${DB_CRUD_PASSWORD}';
  END IF;
END
\\\$\\\$;

-- Grant CRUD limited privileges
GRANT CONNECT ON DATABASE ${db_name} TO ${DB_CRUD_USERNAME};
SQLEOF
)

  # DB-specific grants (must run connected to the target database)
  local db_grants
  db_grants=$(cat << GRANTSEOF
-- Admin: full schema privileges
GRANT ALL PRIVILEGES ON SCHEMA public TO ${DB_ADMIN_USERNAME};
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${DB_ADMIN_USERNAME};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${DB_ADMIN_USERNAME};
ALTER DEFAULT PRIVILEGES FOR USER ${DB_ADMIN_USERNAME} GRANT ALL PRIVILEGES ON TABLES TO ${DB_ADMIN_USERNAME};
ALTER DEFAULT PRIVILEGES FOR USER ${DB_ADMIN_USERNAME} GRANT ALL PRIVILEGES ON SEQUENCES TO ${DB_ADMIN_USERNAME};

-- CRUD: limited privileges (SELECT, INSERT, UPDATE, DELETE only)
GRANT USAGE ON SCHEMA public TO ${DB_CRUD_USERNAME};
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ${DB_CRUD_USERNAME};
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ${DB_CRUD_USERNAME};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${DB_CRUD_USERNAME};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO ${DB_CRUD_USERNAME};
REVOKE CREATE ON SCHEMA public FROM ${DB_CRUD_USERNAME};
GRANTSEOF
)

  # Execute via SSH jump through gateway
  ssh ${SSH_OPTS} -A -J ${GATEWAY_USER}@${GATEWAY_PUBLIC_IP} ${GATEWAY_USER}@${target_ip} << EOF
    # Run SQL commands on the postgres container
    docker exec -i \$(docker ps -qf "name=postgres" -f "status=running" | head -1) psql -U postgres << 'SQL'
${sql_commands}
SQL

    # Run DB-specific grants
    docker exec -i \$(docker ps -qf "name=postgres" -f "status=running" | head -1) psql -U postgres -d ${db_name} << 'SQL'
${db_grants}
SQL
EOF

  if [ $? -eq 0 ]; then
    info "  ✓ ${svc_name}: roles configured successfully"
  else
    error "  ✗ ${svc_name}: failed to configure roles"
    return 1
  fi
}

# --- Main ---
echo "============================================="
echo "  CMV Infrastructure – DB Role Setup"
echo "============================================="
echo ""

ERRORS=0
for svc_entry in "${SERVICES[@]}"; do
  svc_name="${svc_entry%%:*}"
  db_name="${svc_entry##*:}"
  
  if [ -z "${SERVICE_IPS[$svc_name]:-}" ]; then
    warn "Skipping ${svc_name} (no IP resolved)"
    continue
  fi
  
  configure_db_roles "$svc_name" "$db_name" "${SERVICE_IPS[$svc_name]}" || ((ERRORS++))
  echo ""
done

if [ "$ERRORS" -gt 0 ]; then
  error "${ERRORS} service(s) failed. Check the logs above."
  exit 1
fi

info "All database roles configured successfully!"
