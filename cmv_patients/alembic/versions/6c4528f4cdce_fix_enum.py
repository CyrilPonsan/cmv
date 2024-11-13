"""fix enum

Revision ID: 6c4528f4cdce
Revises: 04d4836b1a09
Create Date: 2024-11-11 03:08:40.104236

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "6c4528f4cdce"
down_revision: Union[str, None] = "04d4836b1a09"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the new enum type
    op.execute("ALTER TYPE documenttype RENAME TO documenttype_old")
    op.execute("""
        CREATE TYPE documenttype AS ENUM (
            'HEALTH_INSURANCE_CARD_CERTIFICATE',
            'AUTHORIZATION_FOR_CARE',
            'AUTHORIZATION_FOR_TREATMENT',
            'AUTHORIZATION_FOR_VISIT',
            'AUTHORIZATION_FOR_OVERNIGHT_STAY',
            'AUTHORIZATION_FOR_DEPARTURE',
            'AUTHORIZATION_FOR_DISCONNECTION',
            'MISCELLANEOUS'
        )
    """)

    # Update the column to use the new enum type
    op.execute(
        "ALTER TABLE document ALTER COLUMN type_document TYPE documenttype USING type_document::text::documenttype"
    )

    # Drop the old enum type
    op.execute("DROP TYPE documenttype_old")


def downgrade() -> None:
    pass
