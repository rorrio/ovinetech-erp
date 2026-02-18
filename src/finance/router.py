from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from typing import List, Dict, Any

from src.shared.database import get_session
from src.finance.models import Transaccion, TransaccionCreate, MetaCapital, MetaCapitalCreate, TipoTransaccion

router = APIRouter(prefix="/finance", tags=["Finance"])

@router.post("/transactions/", response_model=Transaccion)
def create_transaction(transaction: TransaccionCreate, session: Session = Depends(get_session)):
    db_transaction = Transaccion.model_validate(transaction)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction

@router.post("/goals/", response_model=MetaCapital)
def create_goal(goal: MetaCapitalCreate, session: Session = Depends(get_session)):
    db_goal = MetaCapital.model_validate(goal)
    session.add(db_goal)
    session.commit()
    session.refresh(db_goal)
    return db_goal

@router.get("/summary/")
def get_financial_summary(session: Session = Depends(get_session)) -> Dict[str, Any]:
    # 1. Calcular Balance Total (Ingresos - Gastos)
    ingresos = session.exec(select(func.sum(Transaccion.monto)).where(Transaccion.tipo == TipoTransaccion.INGRESO)).one() or 0.0
    gastos = session.exec(select(func.sum(Transaccion.monto)).where(Transaccion.tipo == TipoTransaccion.GASTO)).one() or 0.0
    total_ahorrado = ingresos - gastos

    # 2. Obtener Meta Activa (Tomamos la última creada como ejemplo, o la más cercana)
    # Por simplicidad, tomamos la última meta registrada.
    meta = session.exec(select(MetaCapital).order_by(MetaCapital.id.desc())).first()
    
    progreso_pct = 0.0
    meta_info = None

    if meta:
        if meta.monto_objetivo > 0:
            progreso_pct = (total_ahorrado / meta.monto_objetivo) * 100
            # Cap at 100% just for display logic if needed, but raw value is better
        
        meta_info = {
            "nombre": meta.nombre_objetivo,
            "objetivo": meta.monto_objetivo,
            "limite": meta.fecha_limite,
            "progreso_pct": round(progreso_pct, 1)
        }

    return {
        "balance_total": total_ahorrado,
        "total_ingresos": ingresos,
        "total_gastos": gastos,
        "meta_activa": meta_info
    }
