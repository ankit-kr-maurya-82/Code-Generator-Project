from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select, delete
from db import engine
from models.history import HistoryItem

router = APIRouter(prefix="/history")


@router.get("/")
def get_history():
    with Session(engine) as session:
        statement = select(HistoryItem).order_by(HistoryItem.created_at.desc())
        items = session.exec(statement).all()
        return items


@router.post("/clear")
def clear_history():
    try:
        with Session(engine) as session:
            session.exec(delete(HistoryItem))
            session.commit()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
