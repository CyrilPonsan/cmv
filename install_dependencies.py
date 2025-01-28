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


def install_python_deps(service_path):
    """Installe les dépendances Python pour un service"""
    print(f"\n📦 Installation des dépendances Python pour {Path(service_path).name}...")
    run_command(
        "source venv/bin/activate && pip install -r requirements.txt", cwd=service_path
    )


def install_node_deps(service_path):
    """Installe les dépendances Node.js pour un service"""
    print(
        f"\n📦 Installation des dépendances Node.js pour {Path(service_path).name}..."
    )
    run_command("npm install", cwd=service_path)


def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))

    print("🚀 Début de l'installation des dépendances...")

    # Installation des dépendances racine
    print("\n📦 Installation des dépendances racine...")
    run_command("npm install", cwd=root_dir)

    # Services Python
    python_services = ["cmv_gateway/cmv_back", "cmv_patients", "cmv_chambres"]

    for service in python_services:
        service_path = os.path.join(root_dir, service)
        install_python_deps(service_path)

    # Frontend
    frontend_path = os.path.join(root_dir, "cmv_gateway/cmv_front")
    install_node_deps(frontend_path)

    print("\n✨ Installation des dépendances terminée avec succès!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Une erreur s'est produite: {str(e)}")
        sys.exit(1)
