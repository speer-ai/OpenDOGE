from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from app.db.base_class import Base

class Award(Base):
    """Model for storing USAspending award data"""
    __tablename__ = "awards"

    id = Column(Integer, primary_key=True, index=True)
    award_id = Column(String, unique=True, index=True)
    description = Column(String)
    award_amount = Column(Float)
    recipient_name = Column(String)
    awarding_agency = Column(String)
    funding_agency = Column(String)
    award_type = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    recipient_state = Column(String)
    raw_data = Column(JSON)  # Store complete API response
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 