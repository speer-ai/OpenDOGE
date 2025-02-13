from sqlalchemy import Column, String, DateTime, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class TimeStampedBase(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Contract(TimeStampedBase):
    __tablename__ = "contracts"

    notice_id = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(String)
    agency = Column(String)
    posted_date = Column(DateTime)
    response_deadline = Column(DateTime)
    status = Column(String)
    award_amount = Column(Float, nullable=True)
    contractor_duns = Column(String, nullable=True)
    contractor_name = Column(String, nullable=True)
    raw_data = Column(JSON)  # Store complete API response

class Contractor(TimeStampedBase):
    __tablename__ = "contractors"

    duns = Column(String, unique=True, index=True)
    cage_code = Column(String, nullable=True)
    name = Column(String)
    address = Column(JSON)
    status = Column(String)
    expiration_date = Column(DateTime, nullable=True)
    raw_data = Column(JSON)
    
    # Relationship with USSpending awards
    uspending_awards = relationship("Award", back_populates="recipient") 

# Import USSpending models to ensure they're part of the same metadata
from app.models.schemas.spending import Award, Subaward, FederalAccount, AgencySpending, StateSpending 