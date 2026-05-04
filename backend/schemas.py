from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator


class TagBase(BaseModel):
    name: str
    color: str = '#6366f1'


class TagCreate(TagBase):
    pass


class TagOut(TagBase):
    id: int

    class Config:
        from_attributes = True


class CardBase(BaseModel):
    question: str
    answer: str
    tag_ids: list[int] = []


class CardCreate(CardBase):
    pass


class CardUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    tag_ids: Optional[list[int]] = None


class CardOut(BaseModel):
    id: int
    question: str
    answer: str
    ease_factor: float
    interval_days: int
    next_review_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    tags: list[TagOut] = []

    class Config:
        from_attributes = True

    @field_validator('next_review_at', 'created_at', 'updated_at', mode='before')
    @classmethod
    def serialize_datetime(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat()
        return v


class ReviewSubmit(BaseModel):
    rating: str  # familiar / unsure / forgot


class ReviewLogOut(BaseModel):
    id: int
    card_id: int
    rating: str
    reviewed_at: str

    class Config:
        from_attributes = True

    @field_validator('reviewed_at', mode='before')
    @classmethod
    def serialize_datetime(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat()
        return v


class ReviewGroup(BaseModel):
    cards: list[CardOut]
    has_more: bool
    total_due: int


class StatsOut(BaseModel):
    total_cards: int
    due_cards: int
    reviewed_today: int
    retention_rate: float = 0.0
    streak_days: int = 0
