from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Tabel pivot many-to-many antara lomba dan tags
lomba_tags = db.Table(
    'lomba_tags',
    db.Column('lomba_id', db.Integer, db.ForeignKey('lomba.id', ondelete="CASCADE"), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True)
)

class Lomba(db.Model):
    __tablename__ = 'lomba'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    source_url = db.Column(db.String, nullable=False, unique=True)
    raw_description = db.Column(db.Text)
    organizer = db.Column(db.String)
    registration_start = db.Column(db.Date)
    registration_end = db.Column(db.Date)
    event_start = db.Column(db.Date)
    event_end = db.Column(db.Date)
    is_free = db.Column(db.Boolean)
    price_details = db.Column(db.Text)
    location = db.Column(db.String)
    location_details = db.Column(db.Text)
    registration_link = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relasi many-to-many dengan Tag
    tags = db.relationship(
        'Tag',
        secondary=lomba_tags,
        back_populates='lombas'
    )

class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    # relasi many-to-many dengan Lomba
    lombas = db.relationship(
        'Lomba',
        secondary=lomba_tags,
        back_populates='tags'
    )