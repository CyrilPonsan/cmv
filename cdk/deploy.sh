#!/usr/bin/env bash
# =============================================================================
# CMV Infrastructure CDK Deployment Script
# Validates configuration and deploys the CDK stack to AWS.
#
# Requirements: 4.4 (validate configuration before deployment)
# Requirements: 4.5 (clear error messages for invalid configurations)
# =============================================================================

set -euo pipefail

# --- Colors for output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- Helper functions ---
info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# --- Resolve script directory (works even when called via symlink) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# =============================================================================
# 1. Check prerequisites
# =============================================================================
check_prerequisites() {
  info "Checking prerequisites..."
  local missing=0

  # Node.js
  if ! command -v node &>/dev/null; then
    error "Node.js is not installed. Install Node.js 18+ from https://nodejs.org/"
    missing=1
  else
    NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
      error "Node.js version 18+ is required. Current version: $(node -v)"
      missing=1
    else
      info "  Node.js $(node -v) ✓"
    fi
  fi

  # npm
  if ! command -v npm &>/dev/null; then
    error "npm is not installed. It should come with Node.js."
    missing=1
  else
    info "  npm $(npm -v) ✓"
  fi

  # AWS CLI
  if ! command -v aws &>/dev/null; then
    error "AWS CLI is not installed. Install it from https://aws.amazon.com/cli/"
    missing=1
  else
    info "  AWS CLI $(aws --version 2>&1 | awk '{print $1}') ✓"
  fi

  # CDK CLI
  if ! command -v cdk &>/dev/null; then
    warn "AWS CDK CLI is not installed globally. Will use npx cdk instead."
    CDK_CMD="npx cdk"
  else
    info "  CDK CLI $(cdk --version 2>&1 | awk '{print $1}') ✓"
    CDK_CMD="cdk"
  fi

  if [ "$missing" -ne 0 ]; then
    error "Missing prerequisites. Please install the tools listed above and try again."
    exit 1
  fi

  info "All prerequisites satisfied."
}

# =============================================================================
# 2. Validate environment file
# =============================================================================
validate_env_file() {
  info "Validating environment configuration..."

  local env_file="${SCRIPT_DIR}/.env"
  local env_example="${SCRIPT_DIR}/.env.example"

  if [ ! -f "$env_file" ]; then
    error ".env file not found at ${env_file}"
    if [ -f "$env_example" ]; then
      error "Copy the example file and fill in your values:"
      error "  cp ${env_example} ${env_file}"
    fi
    exit 1
  fi

  # Source the .env file
  set -a
  # shellcheck disable=SC1090
  source "$env_file"
  set +a

  local missing_vars=0

  # Required variables
  REQUIRED_VARS=(
    "CDK_DEFAULT_ACCOUNT"
    "CDK_DEFAULT_REGION"
    "DB_ADMIN_USERNAME"
    "DB_ADMIN_PASSWORD"
    "DB_CRUD_USERNAME"
    "DB_CRUD_PASSWORD"
    "DB_NAME"
    "SECRET_KEY"
  )

  for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
      error "Required environment variable ${var} is not set or empty."
      missing_vars=1
    fi
  done

  if [ "$missing_vars" -ne 0 ]; then
    error "Missing required environment variables. Check your .env file against .env.example."
    exit 1
  fi

  # Validate AWS account ID format (12-digit number)
  if ! [[ "$CDK_DEFAULT_ACCOUNT" =~ ^[0-9]{12}$ ]]; then
    error "CDK_DEFAULT_ACCOUNT must be a 12-digit AWS account ID. Got: '${CDK_DEFAULT_ACCOUNT}'"
    exit 1
  fi

  # Validate AWS region format
  if ! [[ "$CDK_DEFAULT_REGION" =~ ^[a-z]{2}-[a-z]+-[0-9]+$ ]]; then
    error "CDK_DEFAULT_REGION must be a valid AWS region (e.g. eu-west-1). Got: '${CDK_DEFAULT_REGION}'"
    exit 1
  fi

  # Warn about default/weak passwords
  if [ "$DB_ADMIN_PASSWORD" = "secure_admin_password_here" ] || [ "$DB_ADMIN_PASSWORD" = "secure_admin_password_123" ]; then
    warn "DB_ADMIN_PASSWORD appears to be a placeholder. Use a strong password for production."
  fi

  if [ "$DB_CRUD_PASSWORD" = "secure_crud_password_here" ] || [ "$DB_CRUD_PASSWORD" = "secure_crud_password_456" ]; then
    warn "DB_CRUD_PASSWORD appears to be a placeholder. Use a strong password for production."
  fi

  info "Environment configuration is valid."
}

# =============================================================================
# 3. Install dependencies
# =============================================================================
install_dependencies() {
  info "Checking dependencies..."

  if [ ! -d "${SCRIPT_DIR}/node_modules" ]; then
    info "Installing npm dependencies..."
    npm install --prefix "$SCRIPT_DIR"
  else
    info "  node_modules exists. Skipping install (run 'npm install' manually to update)."
  fi
}

# =============================================================================
# 4. Build TypeScript
# =============================================================================
build_project() {
  info "Building TypeScript..."
  npm run build --prefix "$SCRIPT_DIR"
  info "Build succeeded."
}

# =============================================================================
# 5. CDK Bootstrap (if needed)
# =============================================================================
bootstrap_cdk() {
  info "Checking CDK bootstrap status..."

  # Try to detect if bootstrap is needed by checking for the CDKToolkit stack
  if aws cloudformation describe-stacks --stack-name CDKToolkit --region "$CDK_DEFAULT_REGION" &>/dev/null; then
    info "  CDK is already bootstrapped in ${CDK_DEFAULT_REGION}."
  else
    info "  Bootstrapping CDK in account ${CDK_DEFAULT_ACCOUNT} / region ${CDK_DEFAULT_REGION}..."
    $CDK_CMD bootstrap "aws://${CDK_DEFAULT_ACCOUNT}/${CDK_DEFAULT_REGION}" --app "npx ts-node ${SCRIPT_DIR}/bin/cdk.ts"
  fi
}

# =============================================================================
# 6. Deploy
# =============================================================================
deploy_stack() {
  info "Deploying CmvInfrastructureStack..."
  $CDK_CMD deploy --app "npx ts-node ${SCRIPT_DIR}/bin/cdk.ts" --require-approval broadening "$@"
  info "Deployment complete!"
}

# =============================================================================
# Main
# =============================================================================
main() {
  echo "============================================="
  echo "  CMV Infrastructure – CDK Deployment"
  echo "============================================="
  echo ""

  check_prerequisites
  echo ""
  validate_env_file
  echo ""
  install_dependencies
  echo ""
  build_project
  echo ""
  bootstrap_cdk
  echo ""
  deploy_stack "$@"
}

main "$@"
