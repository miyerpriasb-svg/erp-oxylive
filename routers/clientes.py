from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from collections import Counter
import models
from database import get_db

router = APIRouter(prefix="/clientes", tags=["Modulo de Clientes"])


def hora_actual():
    return (datetime.utcnow() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")


def segmento_por_interacciones(total: int) -> str:
    if total >= 5:
        return "Frecuente"
    if total >= 2:
        return "Esporadico"
    return "Nuevo"


class ClienteNuevo(BaseModel):
    razon_social: str
    tipo_cliente: str = "Juridico"
    nit: str
    correo: Optional[str] = ""
    telefono: Optional[str] = ""


class InteraccionNueva(BaseModel):
    tipo: str
    detalle: Optional[str] = ""


@router.get("/")
def obtener_clientes(db: Session = Depends(get_db)):
    clientes = db.query(models.Cliente).order_by(models.Cliente.id.desc()).all()
    resultado = []
    for cliente in clientes:
        interacciones = db.query(models.InteraccionCliente).filter(
            models.InteraccionCliente.cliente_id == cliente.id
        ).all()
        tipos = Counter([i.tipo for i in interacciones])
        total = len(interacciones)
        resultado.append({
            "id": cliente.id,
            "razon_social": cliente.razon_social,
            "tipo_cliente": cliente.tipo_cliente or "Juridico",
            "nit": cliente.nit,
            "correo": cliente.correo or "",
            "telefono": cliente.telefono or "",
            "total_interacciones": total,
            "segmento": segmento_por_interacciones(total),
            "tipos_interaccion": dict(tipos),
        })
    return resultado


@router.post("/")
def crear_cliente(cliente: ClienteNuevo, db: Session = Depends(get_db)):
    nuevo = models.Cliente(
        razon_social=cliente.razon_social,
        tipo_cliente=cliente.tipo_cliente,
        nit=cliente.nit,
        correo=cliente.correo,
        telefono=cliente.telefono,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    db.add(models.InteraccionCliente(
        cliente_id=nuevo.id,
        tipo="Alta de cliente",
        detalle="Cliente creado en el directorio",
        fecha=hora_actual(),
    ))
    db.commit()
    return {"mensaje": f"Cliente {cliente.razon_social} registrado."}


@router.post("/{cliente_id}/interacciones")
def crear_interaccion(cliente_id: int, interaccion: InteraccionNueva, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    nueva = models.InteraccionCliente(
        cliente_id=cliente_id,
        tipo=interaccion.tipo,
        detalle=interaccion.detalle or "",
        fecha=hora_actual(),
    )
    db.add(nueva)
    db.commit()
    return {"mensaje": "Interaccion registrada"}


@router.get("/{cliente_id}/interacciones")
def obtener_interacciones(cliente_id: int, db: Session = Depends(get_db)):
    return db.query(models.InteraccionCliente).filter(
        models.InteraccionCliente.cliente_id == cliente_id
    ).order_by(models.InteraccionCliente.id.desc()).all()


@router.get("/crm/resumen")
def resumen_clientes(db: Session = Depends(get_db)):
    clientes = obtener_clientes(db)
    por_segmento = Counter([c["segmento"] for c in clientes])
    por_tipo_cliente = Counter([c["tipo_cliente"] for c in clientes])
    por_tipo_interaccion = Counter()
    for cliente in clientes:
        por_tipo_interaccion.update(cliente["tipos_interaccion"])
    return {
        "total_clientes": len(clientes),
        "total_interacciones": sum(c["total_interacciones"] for c in clientes),
        "por_segmento": dict(por_segmento),
        "por_tipo_cliente": dict(por_tipo_cliente),
        "por_tipo_interaccion": dict(por_tipo_interaccion),
        "clientes": clientes,
    }
