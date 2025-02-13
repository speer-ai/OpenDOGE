from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.government_data import (
    ContractOpportunity,
    Subaward,
    EconomicIndicator,
    CompanyFiling,
    CompanyFinancial
)

router = APIRouter()

@router.get("/contract-opportunities", response_model=List[dict])
async def get_contract_opportunities(
    agency: Optional[str] = None,
    status: Optional[str] = None,
    naics_code: Optional[str] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    posted_after: Optional[datetime] = None,
    posted_before: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Get contract opportunities with optional filters"""
    query = select(ContractOpportunity)
    
    if agency:
        query = query.where(ContractOpportunity.agency == agency)
    if status:
        query = query.where(ContractOpportunity.status == status)
    if naics_code:
        query = query.where(ContractOpportunity.naics_code == naics_code)
    if min_value:
        query = query.where(ContractOpportunity.estimated_value >= min_value)
    if max_value:
        query = query.where(ContractOpportunity.estimated_value <= max_value)
    if posted_after:
        query = query.where(ContractOpportunity.posted_date >= posted_after)
    if posted_before:
        query = query.where(ContractOpportunity.posted_date <= posted_before)
    
    result = await db.execute(query)
    opportunities = result.scalars().all()
    return [opp.__dict__ for opp in opportunities]

@router.get("/subawards", response_model=List[dict])
async def get_subawards(
    prime_award_id: Optional[str] = None,
    recipient_name: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    performance_start_after: Optional[datetime] = None,
    performance_start_before: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Get subawards with optional filters"""
    query = select(Subaward)
    
    if prime_award_id:
        query = query.where(Subaward.prime_award_id == prime_award_id)
    if recipient_name:
        query = query.where(Subaward.recipient_name.ilike(f"%{recipient_name}%"))
    if min_amount:
        query = query.where(Subaward.amount >= min_amount)
    if max_amount:
        query = query.where(Subaward.amount <= max_amount)
    if performance_start_after:
        query = query.where(Subaward.period_of_performance_start >= performance_start_after)
    if performance_start_before:
        query = query.where(Subaward.period_of_performance_start <= performance_start_before)
    
    result = await db.execute(query)
    subawards = result.scalars().all()
    return [sub.__dict__ for sub in subawards]

@router.get("/economic-indicators", response_model=List[dict])
async def get_economic_indicators(
    series_id: Optional[str] = None,
    indicator_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Get economic indicators with optional filters"""
    query = select(EconomicIndicator)
    
    if series_id:
        query = query.where(EconomicIndicator.series_id == series_id)
    if indicator_type:
        query = query.where(EconomicIndicator.indicator_type == indicator_type)
    if start_date:
        query = query.where(EconomicIndicator.date >= start_date)
    if end_date:
        query = query.where(EconomicIndicator.date <= end_date)
    
    result = await db.execute(query)
    indicators = result.scalars().all()
    return [ind.__dict__ for ind in indicators]

@router.get("/company-filings", response_model=List[dict])
async def get_company_filings(
    cik: Optional[str] = None,
    company_name: Optional[str] = None,
    filing_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    fiscal_year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get company filings with optional filters"""
    query = select(CompanyFiling)
    
    if cik:
        query = query.where(CompanyFiling.cik == cik)
    if company_name:
        query = query.where(CompanyFiling.company_name.ilike(f"%{company_name}%"))
    if filing_type:
        query = query.where(CompanyFiling.filing_type == filing_type)
    if start_date:
        query = query.where(CompanyFiling.filing_date >= start_date)
    if end_date:
        query = query.where(CompanyFiling.filing_date <= end_date)
    if fiscal_year:
        query = query.where(CompanyFiling.fiscal_year == fiscal_year)
    
    result = await db.execute(query)
    filings = result.scalars().all()
    return [filing.__dict__ for filing in filings]

@router.get("/company-financials/{filing_id}", response_model=List[dict])
async def get_company_financials(
    filing_id: int,
    metric_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get financial metrics for a specific filing"""
    query = select(CompanyFinancial).where(CompanyFinancial.filing_id == filing_id)
    
    if metric_name:
        query = query.where(CompanyFinancial.metric_name == metric_name)
    
    result = await db.execute(query)
    financials = result.scalars().all()
    if not financials:
        raise HTTPException(status_code=404, detail="Filing not found")
    
    return [fin.__dict__ for fin in financials] 