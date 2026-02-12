from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from src.shared.database import get_session
from src.greenhouse.models import FVHCiclo, FVHCicloCreate, FVHCosecha, FVHCosechaCreate

router = APIRouter(prefix="/greenhouse", tags=["GreenHouse"])

@router.post("/cycles/", response_model=FVHCiclo)
def create_cycle(cycle_data: FVHCicloCreate, session: Session = Depends(get_session)):
    cycle = FVHCiclo.model_validate(cycle_data)
    session.add(cycle)
    session.commit()
    session.refresh(cycle)
    return cycle

@router.get("/cycles/", response_model=List[FVHCiclo])
def read_cycles(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    cycles = session.exec(select(FVHCiclo).offset(skip).limit(limit)).all()
    return cycles

@router.post("/harvests/", response_model=FVHCosecha)
def create_harvest(harvest_data: FVHCosechaCreate, session: Session = Depends(get_session)):
    # Validate cycle exists
    cycle = session.get(FVHCiclo, harvest_data.ciclo_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="FVH Cycle not found")
        
    harvest = FVHCosecha.model_validate(harvest_data)
    session.add(harvest)
    session.commit()
    session.refresh(harvest)
    return harvest
