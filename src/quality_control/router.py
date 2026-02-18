from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from..database import get_session
from.models import RegistroSaneamiento, ControlAgua, ControlPlagas

router = APIRouter(prefix="/quality", tags=["QualityControl"])

@router.post("/saneamiento/", response_model=RegistroSaneamiento)
def crear_registro_saneamiento(registro: RegistroSaneamiento, session: Session = Depends(get_session)):
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return registro

@router.get("/saneamiento/", response_model=List)
def listar_saneamientos(session: Session = Depends(get_session)):
    return session.exec(select(RegistroSaneamiento)).all()

@router.post("/control-agua/", response_model=ControlAgua)
def registrar_control_agua(control: ControlAgua, session: Session = Depends(get_session)):
    # Validación normativa: El cloro debe estar idealmente entre 0.3 y 1.5 ppm
    session.add(control)
    session.commit()
    session.refresh(control)
    return control