#!/usr/bin/env python3
"""
Script pour injecter les fixtures dans les containers Docker.
Usage: python3 run_fixtures_docker.py
"""

import subprocess
import sys


def run_command(command, description):
    """Exécute une commande et affiche le résultat."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout)
        print(f"✅ {description} - OK")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ERREUR")
        if e.stderr:
            print(f"   {e.stderr}")
        return False


def main():
    print("=" * 50)
    print("🚀 Injection des fixtures dans les containers Docker")
    print("=" * 50)

    # Vérifier que les containers tournent
    print("\n📋 Vérification des containers...")
    result = subprocess.run(
        "docker ps --format '{{.Names}}'", shell=True, capture_output=True, text=True
    )
    running_containers = result.stdout.strip().split("\n")

    required = ["cmv_gateway", "cmv_patients", "cmv_chambres"]
    missing = [c for c in required if c not in running_containers]

    if missing:
        print(f"❌ Containers manquants: {', '.join(missing)}")
        print("   Lancez d'abord: npm run start:preprod ou docker-compose up")
        sys.exit(1)

    print(f"✅ Containers actifs: {', '.join(required)}")

    # Gateway fixtures
    run_command(
        "docker exec cmv_gateway python3 create_fixtures.py",
        "Fixtures Gateway (users, roles, permissions)",
    )

    # Patients fixtures
    run_command(
        "docker exec cmv_patients python3 create_fixtures_patients.py",
        "Fixtures Patients",
    )

    # Chambres fixtures
    run_command(
        "docker exec cmv_chambres python3 create_fixtures_chambres.py",
        "Fixtures Chambres (services, chambres)",
    )

    print("\n" + "=" * 50)
    print("✅ Fixtures injectées avec succès!")
    print("=" * 50)


if __name__ == "__main__":
    main()
