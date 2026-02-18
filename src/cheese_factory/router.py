from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List

from src.shared.database import get_session
from src.cheese_factory.models import LoteQueso, LoteQuesoCreate

router = APIRouter(prefix="/cheese-factory", tags=["CheeseFactory"])

from src.finance.models import Transaccion, TipoTransaccion
from src.shared.database import get_session

@router.post("/batches/", response_model=LoteQueso)
def create_lote_queso(lote_queso_data: LoteQuesoCreate, session: Session = Depends(get_session)):
    # 1. Crear el Lote
    lote_queso = LoteQueso.model_validate(lote_queso_data)
    session.add(lote_queso)
    
    # 2. Crear Transacción Financiera (GASTO) automática
    # Calculamos el costo total usando la lógica definida en el modelo (aunque aquí accedemos a los datos raw del input)
    costo_total = lote_queso_data.costo_leche_total + lote_queso_data.costo_operativo
    
    if costo_total > 0:
        gasto = Transaccion(
            tipo=TipoTransaccion.GASTO,
            categoria="PRODUCCION_QUESO",
            monto=costo_total,
            descripcion=f"Costos de producción Lote {lote_queso.tipo_queso} ({lote_queso.fecha_elaboracion.date()})"
        )
        session.add(gasto)

    session.commit()
    session.refresh(lote_queso)
    return lote_queso

@router.get("/batches/", response_model=List[LoteQueso])
def read_lotes_queso(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    lotes = session.exec(select(LoteQueso).offset(skip).limit(limit)).all()
    return lotes
