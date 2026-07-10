"""
Database models for Landing Page Generator
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()


class LandingPage(Base):
    """Model for storing generated landing pages"""
    __tablename__ = 'landing_pages'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    industry = Column(String(100))
    language = Column(String(50))
    style = Column(String(100))
    layout = Column(String(100))
    color = Column(String(100))
    cta = Column(String(255))
    logo_url = Column(String(500))
    hero_image_url = Column(String(500))
    html_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'prompt': self.prompt,
            'industry': self.industry,
            'language': self.language,
            'style': self.style,
            'layout': self.layout,
            'color': self.color,
            'cta': self.cta,
            'logo_url': self.logo_url,
            'hero_image_url': self.hero_image_url,
            'html_content': self.html_content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


def get_engine():
    """Create database engine from environment variable"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Fallback to SQLite for development
        database_url = 'sqlite:///landing_pages.db'
    return create_engine(database_url)


def init_db():
    """Initialize database tables"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get database session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()
