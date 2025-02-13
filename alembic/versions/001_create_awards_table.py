"""create awards table

Revision ID: 001
Revises: 
Create Date: 2024-02-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'awards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('award_id', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('award_amount', sa.Float(), nullable=True),
        sa.Column('recipient_name', sa.String(), nullable=True),
        sa.Column('awarding_agency', sa.String(), nullable=True),
        sa.Column('funding_agency', sa.String(), nullable=True),
        sa.Column('award_type', sa.String(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('recipient_state', sa.String(), nullable=True),
        sa.Column('raw_data', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_awards_award_id'), 'awards', ['award_id'], unique=True)
    op.create_index(op.f('ix_awards_id'), 'awards', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_awards_id'), table_name='awards')
    op.drop_index(op.f('ix_awards_award_id'), table_name='awards')
    op.drop_table('awards') 