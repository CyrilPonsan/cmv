"""create outbox table

Revision ID: a1b2c3d4e5f6
Revises: 12425500cff3
Create Date: 2025-07-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '12425500cff3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enum values matching OutboxStatus in models.py
outbox_status_enum = sa.Enum('PENDING', 'COMPLETED', 'FAILED', name='outboxstatus')


def upgrade() -> None:
    op.create_table(
        'outbox',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('compensation_type', sa.String(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('retry_count', sa.Integer(), server_default='0'),
        sa.Column('status', outbox_status_enum, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('last_attempted_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('outbox')
    outbox_status_enum.drop(op.get_bind(), checkfirst=True)
