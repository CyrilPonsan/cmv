"""Script pour mettre à jour le mot de passe d'un utilisateur dans cmv_gateway.

Usage:
    python update_password.py <username> <nouveau_mot_de_passe>
"""

import sys
import os

import bcrypt
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv(
    "GATEWAY_DATABASE_URL",
    "postgresql://postgres:cmv_gateway@localhost:6001/cmv_gateway",
)


def update_password(username: str, new_password: str):
    engine = create_engine(DATABASE_URL)
    hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    with engine.begin() as conn:
        result = conn.execute(
            text('UPDATE "user" SET password = :pwd WHERE username = :uname'),
            {"pwd": hashed, "uname": username},
        )

    if result.rowcount == 0:
        print(f"Aucun utilisateur trouvé avec le username '{username}'")
        sys.exit(1)

    print(f"Mot de passe mis à jour pour '{username}'")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python update_password.py <username> <nouveau_mot_de_passe>")
        sys.exit(1)

    update_password(sys.argv[1], sys.argv[2])
