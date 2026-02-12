from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List

from src.shared.database import get_session
from src.cheese_factory.models import LoteQueso, LoteQuesoCreate

router = APIRouter(prefix="/cheese-factory", tags=["CheeseFactory"])

@router.post("/batches/", response_model=LoteQueso)
def create_lote_queso(lote_queso_data: LoteQuesoCreate, session: Session = Depends(get_session)):
    lote_queso = LoteQueso.model_validate(lote_queso_data)
    session.add(lote_queso)
    session.commit()
    session.refresh(lote_queso)
    return lote_queso

@router.get("/batches/", response_model=List[LoteQueso])
def read_lotes_queso(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    lotes = session.exec(select(LoteQueso).offset(skip).limit(limit)).all()
    return lotes
