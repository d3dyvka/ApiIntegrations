from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from .db import Base


class Request(Base):
    __tablename__ = "requests"
    
    id = Column(Integer, primary_key=True, index=True)
    base_currency = Column(String(3), nullable=False)
    api_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    responses = relationship("Response", back_populates="request", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_requests_created_at', 'created_at'),
    )


class Response(Base):
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id", ondelete="CASCADE"), nullable=False)
    status_code = Column(Integer, nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    request = relationship("Request", back_populates="responses")
    currencies = relationship("Currency", back_populates="response", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_responses_request_id', 'request_id'),
    )


class Currency(Base):
    __tablename__ = "currencies"
    
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id", ondelete="CASCADE"), nullable=False)
    currency_code = Column(String(3), nullable=False)
    rate = Column(Float, nullable=False)
    
    response = relationship("Response", back_populates="currencies")
    
    __table_args__ = (
        Index('idx_currencies_response_id', 'response_id'),
        Index('idx_currencies_code', 'currency_code'),
    )


