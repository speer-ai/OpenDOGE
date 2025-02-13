"""add government data tables

Revision ID: 002
Revises: 001
Create Date: 2024-02-12 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Contract Opportunities table
    op.create_table(
        'contract_opportunities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('opportunity_id', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('agency', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('posted_date', sa.DateTime(), nullable=True),
        sa.Column('response_deadline', sa.DateTime(), nullable=True),
        sa.Column('estimated_value', sa.Float(), nullable=True),
        sa.Column('place_of_performance', sa.String(), nullable=True),
        sa.Column('naics_code', sa.String(), nullable=True),
        sa.Column('set_aside', sa.String(), nullable=True),
        sa.Column('raw_data', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contract_opportunities_id'), 'contract_opportunities', ['id'], unique=False)
    op.create_index(op.f('ix_contract_opportunities_opportunity_id'), 'contract_opportunities', ['opportunity_id'], unique=True)

    # Subawards table
    op.create_table(
        'subawards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subaward_id', sa.String(), nullable=True),
        sa.Column('prime_award_id', sa.String(), nullable=True),
        sa.Column('recipient_name', sa.String(), nullable=True),
        sa.Column('recipient_address', sa.String(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('place_of_performance', sa.String(), nullable=True),
        sa.Column('period_of_performance_start', sa.DateTime(), nullable=True),
        sa.Column('period_of_performance_end', sa.DateTime(), nullable=True),
        sa.Column('raw_data', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subawards_id'), 'subawards', ['id'], unique=False)
    op.create_index(op.f('ix_subawards_subaward_id'), 'subawards', ['subaward_id'], unique=True)
    op.create_index(op.f('ix_subawards_prime_award_id'), 'subawards', ['prime_award_id'], unique=False)

    # Economic Indicators table
    op.create_table(
        'economic_indicators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('series_id', sa.String(), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('indicator_type', sa.String(), nullable=True),
        sa.Column('units', sa.String(), nullable=True),
        sa.Column('seasonally_adjusted', sa.String(), nullable=True),
        sa.Column('raw_data', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_economic_indicators_id'), 'economic_indicators', ['id'], unique=False)
    op.create_index(op.f('ix_economic_indicators_series_id'), 'economic_indicators', ['series_id'], unique=False)
    op.create_index(op.f('ix_economic_indicators_date'), 'economic_indicators', ['date'], unique=False)

    # Company Filings table
    op.create_table(
        'company_filings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cik', sa.String(), nullable=True),
        sa.Column('company_name', sa.String(), nullable=True),
        sa.Column('filing_type', sa.String(), nullable=True),
        sa.Column('filing_date', sa.DateTime(), nullable=True),
        sa.Column('period_end_date', sa.DateTime(), nullable=True),
        sa.Column('fiscal_year', sa.Integer(), nullable=True),
        sa.Column('fiscal_period', sa.String(), nullable=True),
        sa.Column('raw_data', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_company_filings_id'), 'company_filings', ['id'], unique=False)
    op.create_index(op.f('ix_company_filings_cik'), 'company_filings', ['cik'], unique=False)

    # Company Financials table
    op.create_table(
        'company_financials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filing_id', sa.Integer(), nullable=True),
        sa.Column('metric_name', sa.String(), nullable=True),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('raw_data', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['filing_id'], ['company_filings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_company_financials_id'), 'company_financials', ['id'], unique=False)

def downgrade():
    op.drop_table('company_financials')
    op.drop_table('company_filings')
    op.drop_table('economic_indicators')
    op.drop_table('subawards')
    op.drop_table('contract_opportunities') 