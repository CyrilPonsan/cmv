"""traduction enum type de documents

Revision ID: 04d4836b1a09
Revises: 4e2da680ab2c
Create Date: 2024-11-11 01:47:18.697194

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from alembic import op
from app.sql.models import DocumentType  # Import your enum

# revision identifiers, used by Alembic.
revision: str = "04d4836b1a09"
down_revision: Union[str, None] = "4e2da680ab2c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a temporary column with the new enum type
    op.execute("ALTER TABLE document ALTER COLUMN type_document TYPE VARCHAR(50)")

    # Drop the old enum type
    op.execute("DROP TYPE IF EXISTS documenttype")

    # Create the new enum type
    op.execute(
        "CREATE TYPE documenttype AS ENUM " + str(tuple(e.value for e in DocumentType))
    )

    # Convert the column to use the new enum
    op.execute(
        "ALTER TABLE document ALTER COLUMN type_document TYPE documenttype USING type_document::documenttype"
    )


def downgrade() -> None:
    # Add downgrade logic if needed
    pass
