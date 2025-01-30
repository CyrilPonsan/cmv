import os
import subprocess
import sys
from pathlib import Path


def run_command(command, cwd=None):
    """Exécute une commande shell dans le répertoire spécifié"""
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
        print(f"✅ Succès: {command}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de: {command}")
        print(f"Code d'erreur: {e.returncode}")
        raise e


def setup_venv(service_path):
    """Configure l'environnement virtuel pour un service"""
    service_dir = Path(service_path)
    print(f"\n🔧 Configuration de l'environnement virtuel pour {service_dir.name}...")

    venv_path = service_dir / "venv"
    if venv_path.exists():
        print(f"⚠️  Suppression de l'ancien environnement virtuel dans {venv_path}")
        run_command(f"rm -rf {venv_path}")

    run_command("python3.12 -m venv venv", cwd=service_path)
    print(f"✅ Environnement virtuel créé dans {venv_path}")


def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    services = ["cmv_gateway/cmv_back", "cmv_patients", "cmv_chambres"]

    print("🚀 Début de la configuration des environnements virtuels...")

    for service in services:
        service_path = os.path.join(root_dir, service)
        setup_venv(service_path)

    print("\n✨ Configuration des environnements virtuels terminée avec succès!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Une erreur s'est produite: {str(e)}")
        sys.exit(1)
