from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List

from src.shared.database import get_session
from src.ovine_manager.models import LoteOvejas, LoteOvejasCreate, EventoAlimentacion, EventoAlimentacionCreate

router = APIRouter(prefix="/ovine-manager", tags=["OvineManager"])

@router.post("/batches/", response_model=LoteOvejas)
def create_batch(batch_data: LoteOvejasCreate, session: Session = Depends(get_session)):
    batch = LoteOvejas.model_validate(batch_data)
    session.add(batch)
    session.commit()
    session.refresh(batch)
    return batch

@router.get("/batches/", response_model=List[LoteOvejas])
def read_batches(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    batches = session.exec(select(LoteOvejas).offset(skip).limit(limit)).all()
    return batches

@router.post("/feeding-events/", response_model=EventoAlimentacion)
def create_feeding_event(event_data: EventoAlimentacionCreate, session: Session = Depends(get_session)):
    event = EventoAlimentacion.model_validate(event_data)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event
