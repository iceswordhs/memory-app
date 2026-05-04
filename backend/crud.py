from datetime import datetime, date, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from models import Card, Tag, ReviewLog
from schemas import CardCreate, CardUpdate, TagCreate
from algorithm import calculate


# ---- Tags ----

def get_tags(db: Session) -> list[Tag]:
    return db.query(Tag).order_by(Tag.name).all()


def create_tag(db: Session, data: TagCreate) -> Tag:
    tag = Tag(name=data.name, color=data.color)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag_id: int):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()


# ---- Cards ----

def get_cards(db: Session, tag_id: int | None = None) -> list[Card]:
    q = db.query(Card)
    if tag_id is not None:
        q = q.filter(Card.tags.any(Tag.id == tag_id))
    return q.order_by(Card.created_at.desc()).all()


def get_card(db: Session, card_id: int) -> Card | None:
    return db.query(Card).filter(Card.id == card_id).first()


def create_card(db: Session, data: CardCreate) -> Card:
    card = Card(question=data.question, answer=data.answer)
    if data.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(data.tag_ids)).all()
        card.tags = tags
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def update_card(db: Session, card_id: int, data: CardUpdate) -> Card | None:
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        return None
    if data.question is not None:
        card.question = data.question
    if data.answer is not None:
        card.answer = data.answer
    if data.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(data.tag_ids)).all()
        card.tags = tags
    card.updated_at = datetime.now()
    db.commit()
    db.refresh(card)
    return card


def delete_card(db: Session, card_id: int):
    card = db.query(Card).filter(Card.id == card_id).first()
    if card:
        db.delete(card)
        db.commit()


# ---- Review ----

def submit_review(db: Session, card_id: int, rating: str) -> Card | None:
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        return None

    # 计算新的复习参数
    result = calculate(card.ease_factor, card.interval_days, rating)

    card.ease_factor = result['ease_factor']
    card.interval_days = result['interval_days']
    card.next_review_at = result['next_review_at']
    card.updated_at = datetime.now()

    # 记录日志
    log = ReviewLog(card_id=card_id, rating=rating)
    db.add(log)
    db.commit()
    db.refresh(card)
    return card


def get_due_cards(db: Session, limit: int = 3) -> list[Card]:
    now = datetime.now()
    cards = (
        db.query(Card)
        .filter(Card.next_review_at <= now)
        .order_by(Card.next_review_at.asc())
        .limit(limit)
        .all()
    )
    return cards


def get_due_count(db: Session) -> int:
    now = datetime.now()
    return db.query(Card).filter(Card.next_review_at <= now).count()


def get_has_more_due(db: Session, offset: int = 3) -> bool:
    now = datetime.now()
    count = (
        db.query(Card)
        .filter(Card.next_review_at <= now)
        .offset(offset)
        .limit(1)
        .count()
    )
    return count > 0


# ---- Stats ----

def get_stats(db: Session):
    total = db.query(Card).count()

    now = datetime.now()
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())

    due = db.query(Card).filter(Card.next_review_at <= now).count()
    reviewed_today = db.query(ReviewLog).filter(
        ReviewLog.reviewed_at >= today_start,
        ReviewLog.reviewed_at <= today_end,
    ).count()

    # 保留率：今天复习中 familiar 的比例
    today_reviews = db.query(ReviewLog).filter(
        ReviewLog.reviewed_at >= today_start,
        ReviewLog.reviewed_at <= today_end,
    ).all()
    retention = 0.0
    if today_reviews:
        familiar_count = sum(1 for r in today_reviews if r.rating == 'familiar')
        retention = round(familiar_count / len(today_reviews) * 100, 1)

    # 连续学习天数（简化版：往前遍历，有复习的天数）
    streak = _calc_streak(db)

    return {
        'total_cards': total,
        'due_cards': due,
        'reviewed_today': reviewed_today,
        'retention_rate': retention,
        'streak_days': streak,
    }


def _calc_streak(db: Session) -> int:
    """计算连续学习天数"""
    streak = 0
    d = date.today()
    for _ in range(365):
        day_start = datetime.combine(d, datetime.min.time())
        day_end = datetime.combine(d, datetime.max.time())
        count = db.query(ReviewLog).filter(
            ReviewLog.reviewed_at >= day_start,
            ReviewLog.reviewed_at <= day_end,
        ).count()
        if count > 0:
            streak += 1
            d -= timedelta(days=1)
        else:
            break
    return streak
