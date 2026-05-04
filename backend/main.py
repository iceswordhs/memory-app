import os
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import Card, Tag
from schemas import CardCreate, CardUpdate, CardOut, TagCreate, TagOut, ReviewSubmit, ReviewGroup, StatsOut
from crud import (
    get_tags, create_tag, delete_tag,
    get_cards, get_card, create_card, update_card, delete_card,
    submit_review, get_due_cards, get_due_count, get_has_more_due,
    get_stats,
)

app = FastAPI(title="记忆卡片 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.on_event("startup")
def on_startup():
    init_db()


# ---- Tags ----

@app.get("/api/tags", response_model=list[TagOut])
def list_tags(db: Session = Depends(get_db)):
    return get_tags(db)


@app.post("/api/tags", response_model=TagOut)
def add_tag(data: TagCreate, db: Session = Depends(get_db)):
    return create_tag(db, data)


@app.delete("/api/tags/{tag_id}")
def remove_tag(tag_id: int, db: Session = Depends(get_db)):
    delete_tag(db, tag_id)
    return {"ok": True}


# ---- Cards ----

@app.get("/api/cards", response_model=list[CardOut])
def list_cards(tag_id: int = None, db: Session = Depends(get_db)):
    return get_cards(db, tag_id)


@app.get("/api/cards/{card_id}", response_model=CardOut)
def get_card_detail(card_id: int, db: Session = Depends(get_db)):
    card = get_card(db, card_id)
    if not card:
        raise HTTPException(404, "卡片不存在")
    return card


@app.post("/api/cards", response_model=CardOut)
def add_card(data: CardCreate, db: Session = Depends(get_db)):
    return create_card(db, data)


@app.put("/api/cards/{card_id}", response_model=CardOut)
def edit_card(card_id: int, data: CardUpdate, db: Session = Depends(get_db)):
    card = update_card(db, card_id, data)
    if not card:
        raise HTTPException(404, "卡片不存在")
    return card


@app.delete("/api/cards/{card_id}")
def remove_card(card_id: int, db: Session = Depends(get_db)):
    delete_card(db, card_id)
    return {"ok": True}


# ---- 图片上传 ----

@app.post("/api/upload")
def upload_image(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix if file.filename else ".png"
    name = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}{ext}"
    path = UPLOAD_DIR / name
    with open(path, "wb") as f:
        f.write(file.file.read())
    return {"url": f"/uploads/{name}"}


# ---- 复习 ----

@app.get("/api/review/next", response_model=ReviewGroup)
def next_review_group(db: Session = Depends(get_db)):
    cards = get_due_cards(db, limit=3)
    total_due = get_due_count(db)
    return ReviewGroup(
        cards=[CardOut.model_validate(c) for c in cards],
        has_more=total_due > 3,
        total_due=total_due,
    )


@app.post("/api/review/{card_id}")
def review_card(card_id: int, data: ReviewSubmit, db: Session = Depends(get_db)):
    if data.rating not in ("familiar", "unsure", "forgot"):
        raise HTTPException(400, "评级无效，请使用 familiar / unsure / forgot")
    card = submit_review(db, card_id, data.rating)
    if not card:
        raise HTTPException(404, "卡片不存在")
    return CardOut.model_validate(card)


# ---- 统计 ----

@app.get("/api/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    return get_stats(db)
