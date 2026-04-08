"""Initial migration for validated_predictions table

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create validated_predictions table
    # RGPD Compliance: This table does NOT contain any medical features columns
    op.create_table(
        'validated_predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('predicted_value', sa.Float(), nullable=False),
        sa.Column('validation_date', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for efficient querying
    op.create_index('idx_predictions_user_id', 'validated_predictions', ['user_id'], unique=False)
    op.create_index('idx_predictions_validation_date', 'validated_predictions', ['validation_date'], unique=False)


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('idx_predictions_validation_date', table_name='validated_predictions')
    op.drop_index('idx_predictions_user_id', table_name='validated_predictions')
    
    # Drop table
    op.drop_table('validated_predictions')
