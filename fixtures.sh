#!/bin/bash
# Script pour injecter les fixtures dans les containers Docker
# Usage: ./fixtures.sh

echo "🚀 Injection des fixtures..."

echo "📦 Gateway..."
docker exec cmv_gateway python3 create_fixtures.py

echo "📦 Patients..."
docker exec cmv_patients python3 create_fixtures_patients.py

echo "📦 Chambres..."
docker exec cmv_chambres python3 create_fixtures_chambres.py

echo "✅ Terminé!"
