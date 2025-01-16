"""empty message

Revision ID: aabb58550938
Revises: 1b6163bef3a0
Create Date: 2025-01-17 00:25:37.491616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aabb58550938'
down_revision: Union[str, None] = '1b6163bef3a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
