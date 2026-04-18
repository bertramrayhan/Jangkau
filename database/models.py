from sqlalchemy import (
    create_engine, Column, Integer, String, Text, Date, DateTime, Boolean,
    ForeignKey, Table
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

Base = declarative_base()

lomba_tags = Table(
    'lomba_tags', Base.metadata,
    Column('lomba_id', Integer, ForeignKey('lomba.id', ondelete="CASCADE"), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True)
)

class Lomba(Base):
    __tablename__ = 'lomba'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    source_url = Column(String, nullable=False, unique=True)
    content_html = Column(Text)
    organizer = Column(String)
    registration_start = Column(Date)
    registration_end = Column(Date)
    event_start = Column(Date)
    event_end = Column(Date)
    is_free = Column(Boolean)
    price_details = Column(Text)
    location = Column(String)
    location_details = Column(Text)
    registration_link = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tags = relationship(
        'Tag',
        secondary=lomba_tags,
        back_populates='lombas'
    )

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    lombas = relationship(
        'Lomba',
        secondary=lomba_tags,
        back_populates='tags'
    )

def get_engine_and_session(database_url):
    """Membuat engine dan mengembalikan class Session."""
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return engine, Session
