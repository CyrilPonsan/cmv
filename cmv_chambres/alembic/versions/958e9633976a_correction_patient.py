"""correction patient

Revision ID: 958e9633976a
Revises: bd0245210cee
Create Date: 2025-01-18 22:55:38.870514

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '958e9633976a'
down_revision: Union[str, None] = 'bd0245210cee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('chambre_patient_id_fkey', 'chambre', type_='foreignkey')
    op.drop_column('chambre', 'patient_id')
    op.add_column('reservation', sa.Column('entree_prevue', sa.DateTime(), nullable=False))
    op.drop_column('reservation', 'entree_le')
    op.drop_column('reservation', 'sortie_le')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reservation', sa.Column('sortie_le', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.add_column('reservation', sa.Column('entree_le', postgresql.TIMESTAMP(), autoincrement=False, nullable=False))
    op.drop_column('reservation', 'entree_prevue')
    op.add_column('chambre', sa.Column('patient_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('chambre_patient_id_fkey', 'chambre', 'patient', ['patient_id'], ['id_patient'], ondelete='CASCADE')
    # ### end Alembic commands ###
