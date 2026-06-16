from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
import models
from database import get_db

router = APIRouter(prefix="/procesos", tags=["Módulo de Operaciones"])

def hora_actual():
    # Ajuste automático de zona horaria (UTC -5)
    return (datetime.utcnow() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")

class ProcesoNuevo(BaseModel):
    ods: str
    tipo_tarea: str
    id_cliente: int
    id_trabajador_asignado: int

class DiagnosticoData(BaseModel):
    tipo_equipo: str
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
        resultado.append({
            "id": p.id, "ods": p.ods, "tipo_tarea": p.tipo_tarea,
            "cliente": cliente.razon_social if cliente else "N/A",
            "tecnico": tecnico.nombre if tecnico else "N/A",
            "id_trabajador_asignado": p.id_trabajador_asignado,
            "estado": p.estado or "PENDIENTE DIAGNÓSTICO",
            "porcentaje_avance": p.porcentaje_avance or 10,
            "fecha_creacion": p.fecha_creacion,
            "fecha_diagnostico": p.fecha_diagnostico,
            "fecha_aprobacion": p.fecha_aprobacion,
            "fecha_finalizacion": p.fecha_finalizacion
        })
    return resultado

@router.post("/nuevo")
def crear_proceso(proc: ProcesoNuevo, db: Session = Depends(get_db)):
    nuevo = models.Proceso(
        ods=proc.ods, tipo_tarea=proc.tipo_tarea,
        id_cliente=proc.id_cliente, id_trabajador_asignado=proc.id_trabajador_asignado,
        estado="PENDIENTE DIAGNÓSTICO", porcentaje_avance=10,
        fecha_creacion=hora_actual()
    )
    db.add(nuevo)
    db.commit()
    return {"mensaje": "ODS Creada exitosamente."}

@router.post("/{ods_id}/diagnosticar")
def diagnosticar_ods(ods_id: int, diag: DiagnosticoData, db: Session = Depends(get_db)):
    proceso = db.query(models.Proceso).filter(models.Proceso.id == ods_id).first()
    nuevo_diag = models.Diagnostico(
        proceso_id=ods_id, tipo_equipo=diag.tipo_equipo,
        estado_compresor=diag.estado_compresor, estado_tamiz=diag.estado_tamiz,
        estado_valvulas=diag.estado_valvulas, estado_bateria=diag.estado_bateria,
        observaciones=diag.observaciones
    )
    db.add(nuevo_diag)
    proceso.estado = "ESPERANDO APROBACIÓN"
    proceso.porcentaje_avance = 30
    proceso.fecha_diagnostico = hora_actual()
    db.commit()
    return {"mensaje": "Diagnóstico registrado."}

@router.post("/{ods_id}/cambiar-estado")
def cambiar_estado(ods_id: int, accion: str, db: Session = Depends(get_db)):
    proceso = db.query(models.Proceso).filter(models.Proceso.id == ods_id).first()
    if accion == "aprobar":
        proceso.estado = "APROBADO - EN EJECUCIÓN"
        proceso.porcentaje_avance = 60
        proceso.fecha_aprobacion = hora_actual()
        db.commit()
    return {"mensaje": f"ODS actualizada"}

@router.post("/{ods_id}/finalizar")
def finalizar_ods(ods_id: int, data: FinalizarData, db: Session = Depends(get_db)):
    proceso = db.query(models.Proceso).filter(models.Proceso.id == ods_id).first()
    for rep in data.repuestos:
        item = db.query(models.Inventario).filter(models.Inventario.nombre_insumo == rep.nombre_insumo).first()
        if item and item.cantidad_disponible >= rep.cantidad:
            item.cantidad_disponible -= rep.cantidad
            nuevo_uso = models.RepuestoUtilizado(
                proceso_id=ods_id, nombre_repuesto=rep.nombre_insumo,
                cantidad=rep.cantidad, componente_destino="Finalización de ODS"
            )
            db.add(nuevo_uso)
            
    proceso.estado = "FINALIZADO"
    proceso.porcentaje_avance = 100
    proceso.fecha_finalizacion = hora_actual()
    db.commit()
    return {"mensaje": "ODS Finalizada."}

@router.get("/{ods_id}/diagnostico")
def obtener_diagnostico(ods_id: int, db: Session = Depends(get_db)):
    diag = db.query(models.Diagnostico).filter(models.Diagnostico.proceso_id == ods_id).order_by(models.Diagnostico.id.desc()).first()
    if not diag: return {"error": "Diagnóstico no encontrado."}
    return diag