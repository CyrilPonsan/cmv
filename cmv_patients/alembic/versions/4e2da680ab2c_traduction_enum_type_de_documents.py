"""traduction enum type de documents

Revision ID: 4e2da680ab2c
Revises: c389cf62ff0e
Create Date: 2024-11-11 01:28:06.656831

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e2da680ab2c'
down_revision: Union[str, None] = 'c389cf62ff0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
