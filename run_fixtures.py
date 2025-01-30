import os
import subprocess


def run_command(command, cwd=None):
    """Exécute une commande shell dans le répertoire spécifié"""
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
        print(f"✅ Succès: {command}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de: {command}")
        print(f"Code d'erreur: {e.returncode}")
        raise e


def main():
    # Chemin absolu du répertoire racine du projet
    root_dir = os.path.dirname(os.path.abspath(__file__))

    # Gateway fixtures
    gateway_dir = os.path.join(root_dir, "cmv_gateway", "cmv_back")
    run_command(
        "source venv/bin/activate && python3.12 create_fixtures.py", cwd=gateway_dir
    )

    # Patients fixtures
    patients_dir = os.path.join(root_dir, "cmv_patients")
    run_command(
        "source venv/bin/activate && python3.12 create_fixtures_patients.py",
        cwd=patients_dir,
    )

    # Chambres fixtures
    chambres_dir = os.path.join(root_dir, "cmv_chambres")
    run_command(
        "source venv/bin/activate && python3.12 create_fixtures_chambres.py",
        cwd=chambres_dir,
    )


if __name__ == "__main__":
    main()
