from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True, nullable=True) # Added email field

    preferences = relationship("Preference", back_populates="owner")
    news_sources = relationship("NewsSource", back_populates="owner")
    stocks = relationship("Stock", back_populates="owner")
    currencies = relationship("Currency", back_populates="owner")

class Preference(Base):
    __tablename__ = "preferences"
    id = Column(Integer, primary_key=True, index=True)
    email_time = Column(String, default="08:10") # e.g., "08:10"
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="preferences")

class NewsSource(Base):
    __tablename__ = "news_sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="news_sources")

class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True) # e.g., "AAPL", "005930.KS"
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="stocks")

class Currency(Base):
    __tablename__ = "currencies"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True) # e.g., "USD/KRW"
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="currencies")
