"""merge multiple heads

Revision ID: 4b238223d168
Revises: e737a87a2612
Create Date: 2025-01-26 09:52:28.491545

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b238223d168'
down_revision: Union[str, None] = 'e737a87a2612'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
