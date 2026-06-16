from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import models
from database import get_db

router = APIRouter(prefix="/procesos", tags=["Modulo de Operaciones"])


def hora_actual():
    return (datetime.utcnow() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")


def registrar_interaccion_cliente(db: Session, cliente_id: int, tipo: str, detalle: str):
    if cliente_id:
        db.add(models.InteraccionCliente(
            cliente_id=cliente_id,
            tipo=tipo,
            detalle=detalle,
            fecha=hora_actual(),
        ))


class TamizOrdenData(BaseModel):
    marca: str
    cantidad: float
    unidad_conteo: Optional[str] = "Unidad"


class ProcesoNuevo(BaseModel):
    ods: str
    tipo_tarea: str
    tipo_equipo: str = ""
    marca_equipo: str = ""
    modelo_equipo: str = ""
    horas_ingreso: float = 0
    modalidad_servicio: str = ""
    id_cliente: int
    id_trabajador_asignado: int
    tamices: List[TamizOrdenData] = Field(default_factory=list)


class DiagnosticoData(BaseModel):
    estado_compresor: str
    estado_tamiz: str
    estado_valvulas: str
    estado_bateria: str
    observaciones: str


class ParteUsada(BaseModel):
    nombre_insumo: str
    cantidad: float


class FinalizarData(BaseModel):
    repuestos: List[ParteUsada]


@router.get("/")
def obtener_procesos(db: Session = Depends(get_db)):
    procesos = db.query(models.Proceso).order_by(models.Proceso.id.desc()).all()
    resultado = []
    for p in procesos:
        cliente = db.query(models.Cliente).filter(models.Cliente.id == p.id_cliente).first()
        tecnico = db.query(models.Usuario).filter(models.Usuario.id == p.id_trabajador_asignado).first()
        tamices = db.query(models.TamizOrden).filter(models.TamizOrden.proceso_id == p.id).all()
        resultado.append({
            "id": p.id,
            "ods": p.ods,
            "tipo_tarea": p.tipo_tarea,
            "tipo_equipo": p.tipo_equipo or "",
            "marca_equipo": p.marca_equipo or "",
            "modelo_equipo": p.modelo_equipo or "",
            "horas_ingreso": p.horas_ingreso or 0,
            "modalidad_servicio": p.modalidad_servicio or "",
            "cliente": cliente.razon_social if cliente else "N/A",
            "tecnico": tecnico.nombre if tecnico else "N/A",
            "id_trabajador_asignado": p.id_trabajador_asignado,
            "estado": p.estado or "PENDIENTE DIAGNÓSTICO",
            "porcentaje_avance": p.porcentaje_avance or 10,
            "fecha_creacion": p.fecha_creacion,
            "fecha_diagnostico": p.fecha_diagnostico,
            "fecha_aprobacion": p.fecha_aprobacion,
            "fecha_finalizacion": p.fecha_finalizacion,
            "tamices": [
                {
                    "id": t.id,
                    "marca": t.marca or "",
                    "cantidad": t.cantidad or 0,
                    "unidad_conteo": t.unidad_conteo or "Unidad",
                }
                for t in tamices
            ],
        })
    return resultado


@router.post("/nuevo")
def crear_proceso(proc: ProcesoNuevo, db: Session = Depends(get_db)):
    nuevo = models.Proceso(
        ods=proc.ods,
        tipo_tarea=proc.tipo_tarea,
        tipo_equipo=proc.tipo_equipo,
        marca_equipo=proc.marca_equipo,
        modelo_equipo=proc.modelo_equipo,
        horas_ingreso=proc.horas_ingreso,
        modalidad_servicio=proc.modalidad_servicio,
        id_cliente=proc.id_cliente,
        id_trabajador_asignado=proc.id_trabajador_asignado,
        estado="PENDIENTE DIAGNÓSTICO",
        porcentaje_avance=10,
        fecha_creacion=hora_actual(),
    )
    db.add(nuevo)
    db.flush()
    for item in proc.tamices:
        if item.marca or item.cantidad:
            db.add(models.TamizOrden(
                proceso_id=nuevo.id,
                marca=item.marca,
                cantidad=item.cantidad,
                unidad_conteo=item.unidad_conteo or "Unidad",
            ))
    registrar_interaccion_cliente(db, proc.id_cliente, "ODS creada", f"ODS {proc.ods}: {proc.tipo_tarea}")
    db.commit()
    return {"mensaje": "ODS creada exitosamente."}


@router.post("/{ods_id}/diagnosticar")
def diagnosticar_ods(ods_id: int, diag: DiagnosticoData, db: Session = Depends(get_db)):
    proceso = db.query(models.Proceso).filter(models.Proceso.id == ods_id).first()
    if not proceso:
        raise HTTPException(status_code=404, detail="ODS no encontrada")
    nuevo_diag = models.Diagnostico(
        proceso_id=ods_id,
        tipo_equipo=proceso.tipo_equipo or "",
        estado_compresor=diag.estado_compresor,
        estado_tamiz=diag.estado_tamiz,
        estado_valvulas=diag.estado_valvulas,
        estado_bateria=diag.estado_bateria,
        observaciones=diag.observaciones,
    )
    db.add(nuevo_diag)
    registrar_interaccion_cliente(db, proceso.id_cliente, "Diagnostico", f"Diagnostico registrado para {proceso.ods}")
    proceso.estado = "ESPERANDO APROBACIÓN"
    proceso.porcentaje_avance = 30
    proceso.fecha_diagnostico = hora_actual()
    db.commit()
    return {"mensaje": "Diagnostico registrado."}


@router.post("/{ods_id}/cambiar-estado")
def cambiar_estado(ods_id: int, accion: str, db: Session = Depends(get_db)):
    proceso = db.query(models.Proceso).filter(models.Proceso.id == ods_id).first()
    if not proceso:
        raise HTTPException(status_code=404, detail="ODS no encontrada")
    if accion == "aprobar":
        proceso.estado = "APROBADO - EN EJECUCIÓN"
        proceso.porcentaje_avance = 60
        proceso.fecha_aprobacion = hora_actual()
        registrar_interaccion_cliente(db, proceso.id_cliente, "Aprobacion ODS", f"ODS {proceso.ods} aprobada")
        db.commit()
    return {"mensaje": "ODS actualizada"}


@router.post("/{ods_id}/finalizar")
def finalizar_ods(ods_id: int, data: FinalizarData, db: Session = Depends(get_db)):
    proceso = db.query(models.Proceso).filter(models.Proceso.id == ods_id).first()
    if not proceso:
        raise HTTPException(status_code=404, detail="ODS no encontrada")
    for rep in data.repuestos:
        item = db.query(models.Inventario).filter(models.Inventario.nombre_insumo == rep.nombre_insumo).first()
        if item and item.cantidad_disponible >= rep.cantidad:
            item.cantidad_disponible -= rep.cantidad
            db.add(models.RepuestoUtilizado(
                proceso_id=ods_id,
                nombre_repuesto=rep.nombre_insumo,
                cantidad=rep.cantidad,
                componente_destino="Finalizacion de ODS",
            ))
    proceso.estado = "FINALIZADO"
    proceso.porcentaje_avance = 100
    proceso.fecha_finalizacion = hora_actual()
    registrar_interaccion_cliente(db, proceso.id_cliente, "Cierre ODS", f"ODS {proceso.ods} finalizada")
    db.commit()
    return {"mensaje": "ODS finalizada."}


@router.delete("/{ods_id}")
def eliminar_ods(ods_id: int, rol: str, db: Session = Depends(get_db)):
    if (rol or "").upper() != "ADMINISTRADOR":
        raise HTTPException(status_code=403, detail="Solo el administrador puede eliminar ODS")
    proceso = db.query(models.Proceso).filter(models.Proceso.id == ods_id).first()
    if not proceso:
        raise HTTPException(status_code=404, detail="ODS no encontrada")
    db.query(models.Diagnostico).filter(models.Diagnostico.proceso_id == ods_id).delete()
    db.query(models.RepuestoUtilizado).filter(models.RepuestoUtilizado.proceso_id == ods_id).delete()
    db.query(models.TamizOrden).filter(models.TamizOrden.proceso_id == ods_id).delete()
    db.delete(proceso)
    db.commit()
    return {"mensaje": "ODS eliminada"}


@router.get("/{ods_id}/diagnostico")
def obtener_diagnostico(ods_id: int, db: Session = Depends(get_db)):
    diag = db.query(models.Diagnostico).filter(models.Diagnostico.proceso_id == ods_id).order_by(models.Diagnostico.id.desc()).first()
    if not diag:
        return {"error": "Diagnostico no encontrado."}
    return diag
