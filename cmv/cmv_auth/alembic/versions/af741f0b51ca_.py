"""empty message

Revision ID: af741f0b51ca
Revises: 7de78454f611
Create Date: 2024-10-08 13:14:03.784149

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af741f0b51ca'
down_revision: Union[str, None] = '7de78454f611'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
