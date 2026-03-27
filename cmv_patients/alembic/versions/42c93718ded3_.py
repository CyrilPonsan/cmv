"""empty message

Revision ID: 42c93718ded3
Revises: f24d36be25c2
Create Date: 2026-01-16 22:15:50.502737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42c93718ded3'
down_revision: Union[str, None] = 'f24d36be25c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
