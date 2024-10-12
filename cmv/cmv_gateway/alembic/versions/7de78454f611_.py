"""empty message

Revision ID: 7de78454f611
Revises: d3a3a1904546
Create Date: 2024-08-31 01:06:07.939934

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7de78454f611'
down_revision: Union[str, None] = 'd3a3a1904546'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
