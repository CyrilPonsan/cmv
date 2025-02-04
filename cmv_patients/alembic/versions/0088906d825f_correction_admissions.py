"""correction admissions

Revision ID: 0088906d825f
Revises: 4b238223d168
Create Date: 2025-01-26 09:52:49.732748

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0088906d825f'
down_revision: Union[str, None] = '4b238223d168'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('patient',
    sa.Column('id_patient', sa.Integer(), nullable=False),
    sa.Column('civilite', sa.Enum('MONSIEUR', 'MADAME', 'AUTRE', name='civilite'), nullable=False),
    sa.Column('nom', sa.String(), nullable=False),
    sa.Column('prenom', sa.String(), nullable=False),
    sa.Column('date_de_naissance', sa.DateTime(), nullable=False),
    sa.Column('adresse', sa.String(), nullable=False),
    sa.Column('code_postal', sa.String(), nullable=False),
    sa.Column('ville', sa.String(), nullable=False),
    sa.Column('telephone', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id_patient')
    )
    op.create_index(op.f('ix_patient_id_patient'), 'patient', ['id_patient'], unique=False)
    op.create_index(op.f('ix_patient_nom'), 'patient', ['nom'], unique=False)
    op.create_index(op.f('ix_patient_prenom'), 'patient', ['prenom'], unique=False)
    op.create_table('admission',
    sa.Column('id_admission', sa.Integer(), nullable=False),
    sa.Column('entree_le', sa.DateTime(), nullable=False),
    sa.Column('ambulatoire', sa.Boolean(), nullable=False),
    sa.Column('sorti_le', sa.DateTime(), nullable=True),
    sa.Column('sortie_prevue_le', sa.DateTime(), nullable=True),
    sa.Column('ref_chambre', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id_patient'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_admission')
    )
    op.create_index(op.f('ix_admission_id_admission'), 'admission', ['id_admission'], unique=False)
    op.create_table('document',
    sa.Column('id_document', sa.Integer(), nullable=False),
    sa.Column('nom_fichier', sa.String(), nullable=False),
    sa.Column('type_document', sa.Enum('HEALTH_INSURANCE_CARD_CERTIFICATE', 'AUTHORIZATION_FOR_CARE', 'AUTHORIZATION_FOR_TREATMENT', 'AUTHORIZATION_FOR_VISIT', 'AUTHORIZATION_FOR_OVERNIGHT_STAY', 'AUTHORIZATION_FOR_DEPARTURE', 'AUTHORIZATION_FOR_DISCONNECTION', 'MISCELLANEOUS', name='documenttype'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patient.id_patient'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id_document'),
    sa.UniqueConstraint('nom_fichier')
    )
    op.create_index(op.f('ix_document_id_document'), 'document', ['id_document'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_document_id_document'), table_name='document')
    op.drop_table('document')
    op.drop_index(op.f('ix_admission_id_admission'), table_name='admission')
    op.drop_table('admission')
    op.drop_index(op.f('ix_patient_prenom'), table_name='patient')
    op.drop_index(op.f('ix_patient_nom'), table_name='patient')
    op.drop_index(op.f('ix_patient_id_patient'), table_name='patient')
    op.drop_table('patient')
    # ### end Alembic commands ###
