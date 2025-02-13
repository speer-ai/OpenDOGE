from sqlalchemy import Column, String, DateTime, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.database import TimeStampedBase

class Award(TimeStampedBase):
    __tablename__ = "uspending_awards"

    award_id = Column(String, unique=True, index=True)
    generated_unique_award_id = Column(String, unique=True, index=True)
    piid = Column(String, index=True)  # Contract identifier
    fain = Column(String, index=True)  # Financial Assistance Identifier
    award_type = Column(String)
    category = Column(String)
    award_amount = Column(Float)
    total_obligation = Column(Float)
    base_and_all_options_value = Column(Float)
    
    # Dates
    period_of_performance_start_date = Column(DateTime)
    period_of_performance_end_date = Column(DateTime)
    
    # Relationships
    recipient_id = Column(String, ForeignKey('contractors.duns'))
    recipient = relationship("Contractor", back_populates="uspending_awards")
    subawards = relationship("Subaward", back_populates="prime_award")
    
    # Agency information
    awarding_agency_name = Column(String)
    funding_agency_name = Column(String)
    awarding_sub_agency_name = Column(String)
    funding_sub_agency_name = Column(String)
    
    # Additional data
    description = Column(String)
    raw_data = Column(JSON)

class Subaward(TimeStampedBase):
    __tablename__ = "subawards"
    
    subaward_id = Column(String, unique=True, index=True)
    prime_award_id = Column(String, ForeignKey('uspending_awards.generated_unique_award_id'))
    prime_award = relationship("Award", back_populates="subawards")
    
    amount = Column(Float)
    description = Column(String)
    
    # Recipient information
    recipient_name = Column(String)
    recipient_duns = Column(String, index=True)
    recipient_location = Column(JSON)
    
    # Dates
    action_date = Column(DateTime)
    
    raw_data = Column(JSON)

class FederalAccount(TimeStampedBase):
    __tablename__ = "federal_accounts"
    
    account_number = Column(String, unique=True, index=True)
    account_title = Column(String)
    agency_identifier = Column(String)
    main_account_code = Column(String)
    
    # Budgetary Resources
    fiscal_year = Column(Integer)
    budgetary_resources = Column(Float)
    obligations = Column(Float)
    outlays = Column(Float)
    
    # Agency details
    agency_name = Column(String)
    agency_slug = Column(String)
    
    raw_data = Column(JSON)

class AgencySpending(TimeStampedBase):
    __tablename__ = "agency_spending"
    
    agency_id = Column(String, index=True)
    fiscal_year = Column(Integer)
    
    # Spending totals
    total_budgetary_resources = Column(Float)
    total_obligations = Column(Float)
    total_outlays = Column(Float)
    
    # Spending by category
    contracts_spending = Column(Float)
    grants_spending = Column(Float)
    direct_payments_spending = Column(Float)
    loans_spending = Column(Float)
    other_spending = Column(Float)
    
    raw_data = Column(JSON)

class StateSpending(TimeStampedBase):
    __tablename__ = "state_spending"
    
    state_code = Column(String, index=True)
    state_name = Column(String)
    fiscal_year = Column(Integer)
    
    # Award counts
    total_award_count = Column(Integer)
    contract_count = Column(Integer)
    grant_count = Column(Integer)
    
    # Spending amounts
    total_amount = Column(Float)
    contract_amount = Column(Float)
    grant_amount = Column(Float)
    
    # Population and per capita stats
    population = Column(Integer)
    amount_per_capita = Column(Float)
    
    raw_data = Column(JSON)
