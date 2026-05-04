from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, ForeignKey, Table,
)
from sqlalchemy.orm import relationship

from database import Base

card_tags = Table(
    'card_tags', Base.metadata,
    Column('card_id', Integer, ForeignKey('cards.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
)


class Card(Base):
    __tablename__ = 'cards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    ease_factor = Column(Float, default=2.5, nullable=False)
    interval_days = Column(Integer, default=0, nullable=False)
    next_review_at = Column(DateTime, default=datetime.now, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    tags = relationship('Tag', secondary=card_tags, back_populates='cards', lazy='selectin')
    review_logs = relationship('ReviewLog', back_populates='card', lazy='selectin',
                               order_by='ReviewLog.reviewed_at.desc()')

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'ease_factor': self.ease_factor,
            'interval_days': self.interval_days,
            'next_review_at': self.next_review_at.isoformat() if self.next_review_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tags': [t.to_dict() for t in self.tags] if self.tags else [],
        }


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(7), default='#6366f1')

    cards = relationship('Card', secondary=card_tags, back_populates='tags', lazy='selectin')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'color': self.color}


class ReviewLog(Base):
    __tablename__ = 'review_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(Integer, ForeignKey('cards.id', ondelete='CASCADE'), nullable=False)
    rating = Column(String(20), nullable=False)  # familiar / unsure / forgot
    reviewed_at = Column(DateTime, default=datetime.now)

    card = relationship('Card', back_populates='review_logs')

    def to_dict(self):
        return {
            'id': self.id,
            'card_id': self.card_id,
            'rating': self.rating,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
        }
