"""modification de patient, chambre, et reservation

Revision ID: 0ab7c3a68d08
Revises: af37d28983b4
Create Date: 2025-01-18 21:20:13.118956

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0ab7c3a68d08'
down_revision: Union[str, None] = 'af37d28983b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chambre', sa.Column('patient_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'chambre', 'patient', ['patient_id'], ['id_patient'], ondelete='CASCADE')
    op.add_column('patient', sa.Column('chambre_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'patient', 'chambre', ['chambre_id'], ['id_chambre'], ondelete='CASCADE')
    op.add_column('reservation', sa.Column('entree_le', sa.DateTime(), nullable=False))
    op.add_column('reservation', sa.Column('sortie_le', sa.DateTime(), nullable=False))
    op.drop_column('reservation', 'entree_prevue')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reservation', sa.Column('entree_prevue', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.drop_column('reservation', 'sortie_le')
    op.drop_column('reservation', 'entree_le')
    op.drop_constraint(None, 'patient', type_='foreignkey')
    op.drop_column('patient', 'chambre_id')
    op.drop_constraint(None, 'chambre', type_='foreignkey')
    op.drop_column('chambre', 'patient_id')
    # ### end Alembic commands ###
