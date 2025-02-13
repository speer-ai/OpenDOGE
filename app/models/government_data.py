"""Database models for government data sources"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class ContractOpportunity(Base):
    """Model for contract opportunities from FPDS and FBO"""
    __tablename__ = "contract_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(String)
    agency = Column(String)
    status = Column(String)
    posted_date = Column(DateTime)
    response_deadline = Column(DateTime)
    estimated_value = Column(Float)
    place_of_performance = Column(String)
    naics_code = Column(String)
    set_aside = Column(String)
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Subaward(Base):
    """Model for subaward data from FSRS"""
    __tablename__ = "subawards"

    id = Column(Integer, primary_key=True, index=True)
    subaward_id = Column(String, unique=True, index=True)
    prime_award_id = Column(String, index=True)
    recipient_name = Column(String)
    recipient_address = Column(String)
    amount = Column(Float)
    description = Column(String)
    place_of_performance = Column(String)
    period_of_performance_start = Column(DateTime)
    period_of_performance_end = Column(DateTime)
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EconomicIndicator(Base):
    """Model for economic data from FRED"""
    __tablename__ = "economic_indicators"

    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(String, index=True)
    date = Column(DateTime, index=True)
    value = Column(Float)
    indicator_type = Column(String)  # e.g., GDP, Unemployment, etc.
    units = Column(String)  # e.g., Percent, Dollars, etc.
    seasonally_adjusted = Column(String)
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CompanyFiling(Base):
    """Model for SEC EDGAR filings"""
    __tablename__ = "company_filings"

    id = Column(Integer, primary_key=True, index=True)
    cik = Column(String, index=True)
    company_name = Column(String)
    filing_type = Column(String)  # e.g., 10-K, 10-Q, etc.
    filing_date = Column(DateTime)
    period_end_date = Column(DateTime)
    fiscal_year = Column(Integer)
    fiscal_period = Column(String)
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    financials = relationship("CompanyFinancial", back_populates="filing")

class CompanyFinancial(Base):
    """Model for company financial data from SEC"""
    __tablename__ = "company_financials"

    id = Column(Integer, primary_key=True, index=True)
    filing_id = Column(Integer, ForeignKey("company_filings.id"))
    metric_name = Column(String)  # e.g., Assets, Revenue, etc.
    value = Column(Float)
    unit = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    raw_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    filing = relationship("CompanyFiling", back_populates="financials") 