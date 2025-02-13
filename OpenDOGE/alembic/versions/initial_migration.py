"""initial migration

Revision ID: initial
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create contracts table
    op.create_table(
        'contracts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('notice_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('agency', sa.String(), nullable=True),
        sa.Column('posted_date', sa.DateTime(), nullable=True),
        sa.Column('response_deadline', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('award_amount', sa.Float(), nullable=True),
        sa.Column('contractor_duns', sa.String(), nullable=True),
        sa.Column('contractor_name', sa.String(), nullable=True),
        sa.Column('raw_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contracts_notice_id'), 'contracts', ['notice_id'], unique=True)

    # Create contractors table
    op.create_table(
        'contractors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('duns', sa.String(), nullable=True),
        sa.Column('cage_code', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('address', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('expiration_date', sa.DateTime(), nullable=True),
        sa.Column('raw_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contractors_duns'), 'contractors', ['duns'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_contractors_duns'), table_name='contractors')
    op.drop_table('contractors')
    op.drop_index(op.f('ix_contracts_notice_id'), table_name='contracts')
    op.drop_table('contracts') 