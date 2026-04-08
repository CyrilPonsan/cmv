#!/bin/bash
# Applique les migrations Alembic aux 4 bases de données
# en injectant la bonne variable d'env dans chaque container.
#
# Usage: ./migrate_all.sh

set -e

# User PostgreSQL en dur
PG_USER="postgres"

# Config par container : nom | variable d'env attendue par alembic/env.py | URL complète
declare -a SERVICES=(
  "cmv_gateway|AUTH_DATABASE_URL|postgresql://${PG_USER}:cmv_gateway@db_gateway:5432/cmv_gateway"
  "cmv_patients|PATIENTS_DATABASE_URL|postgresql://${PG_USER}:cmv_patients@db_gateway:5432/cmv_patients"
  "cmv_chambres|CHAMBRES_DATABASE_URL|postgresql://${PG_USER}:cmv_chambres@db_gateway:5432/cmv_chambres"
  "cmv_ml|ML_DATABASE_URL|postgresql://${PG_USER}:cmv_ml@db_gateway:5432/cmv_ml"
)

echo "=== Migration Alembic — 4 services ==="

for entry in "${SERVICES[@]}"; do
  IFS='|' read -r container env_var db_url <<< "$entry"

  echo ""
  echo "--- $container ---"

  if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
    echo "⚠  Container $container non trouvé ou arrêté, skip."
    continue
  fi

  docker exec -e "${env_var}=${db_url}" "$container" alembic upgrade head

  if [ $? -eq 0 ]; then
    echo "✓  $container : migrations appliquées"
  else
    echo "✗  $container : échec des migrations"
    exit 1
  fi
done

echo ""
echo "=== Toutes les migrations sont appliquées ==="
