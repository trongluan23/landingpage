"""
Database models for Landing Page Generator
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os
import sys

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
        print("⚠️  DATABASE_URL not set, using SQLite", file=sys.stderr)
        database_url = 'sqlite:///landing_pages.db'
    
    # Fix for Render.com and Heroku: postgres:// -> postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        print(f"🔧 Converted postgres:// to postgresql://", file=sys.stderr)
    
    # Show connection info (hide password)
    if 'postgresql://' in database_url:
        try:
            # Parse to hide password in logs
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            safe_url = f"{parsed.scheme}://{parsed.username}:****@{parsed.hostname}:{parsed.port}{parsed.path}"
            print(f"🔌 Connecting to: {safe_url}", file=sys.stderr)
        except:
            print(f"🔌 Connecting to PostgreSQL", file=sys.stderr)
    else:
        print(f"🔌 Connecting to: {database_url}", file=sys.stderr)
    
    try:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,   # Recycle connections after 1 hour
            echo=False           # Set to True for SQL debugging
        )
        
        # Test connection (SQLAlchemy 2.0 compatible)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print(f"✅ Database connection successful", file=sys.stderr)
        return engine
        
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}", file=sys.stderr)
        
        # If PostgreSQL fails, try SQLite as fallback
        if 'postgresql://' in database_url or 'postgres://' in database_url:
            print(f"⚠️  Falling back to SQLite...", file=sys.stderr)
            fallback_url = 'sqlite:///landing_pages.db'
            return create_engine(fallback_url, pool_pre_ping=True)
        else:
            raise
    except Exception as e:
        print(f"❌ Unexpected database error: {e}", file=sys.stderr)
        raise


def init_db():
    """
    Initialize database tables
    - Auto-creates tables if they don't exist
    - Safe to run multiple times
    """
    try:
        engine = get_engine()
        
        print(f"📋 Creating tables if not exist...", file=sys.stderr)
        Base.metadata.create_all(engine)
        
        print(f"✅ Tables ready", file=sys.stderr)
        return engine
        
    except Exception as e:
        print(f"❌ Table creation failed: {e}", file=sys.stderr)
        raise


def get_session():
    """Get database session"""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

