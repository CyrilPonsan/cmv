"""mise à jour civilités

Revision ID: e737a87a2612
Revises: aabb58550938
Create Date: 2025-01-17 00:25:54.623319

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e737a87a2612"
down_revision: Union[str, None] = "aabb58550938"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Créer une colonne temporaire
    op.execute("ALTER TABLE patient ALTER COLUMN civilite TYPE VARCHAR(50)")

    # Supprimer l'ancien type enum
    op.execute("DROP TYPE IF EXISTS civilite")

    # Créer le nouveau type enum avec les valeurs explicites
    op.execute("""
        CREATE TYPE civilite AS ENUM (
            'Monsieur',
            'Madame',
            'Autre'
        )
    """)

    # Convertir la colonne pour utiliser le nouveau type enum
    op.execute(
        "ALTER TABLE patient ALTER COLUMN civilite TYPE civilite USING civilite::civilite"
    )


def downgrade() -> None:
    pass
