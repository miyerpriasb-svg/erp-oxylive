from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models, datetime
from database import get_db

router = APIRouter(
    prefix="/inventario",
    tags=["Módulo de Inventario"]
)

class ItemNuevo(BaseModel):
    nombre_insumo: str
    cantidad_disponible: float
    unidad_medida: str
    stock_minimo_alerta: float

@router.get("/")
def obtener_inventario(db: Session = Depends(get_db)):
    return db.query(models.Inventario).all()

@router.post("/nuevo")
def crear_item(item: ItemNuevo, db: Session = Depends(get_db)):
    existe = db.query(models.Inventario).filter(models.Inventario.nombre_insumo == item.nombre_insumo).first()
    if existe:
        return {"error": "Este insumo ya existe en la base de datos"}
    
    nuevo_item = models.Inventario(
        nombre_insumo=item.nombre_insumo,
        cantidad_disponible=item.cantidad_disponible,
        unidad_medida=item.unidad_medida,  # <--- CORREGIDO: Sin la línea extra
        stock_minimo_alerta=item.stock_minimo_alerta
    )
    db.add(nuevo_item)
    
    # Grabamos la entrada inicial en el historial de ingresos
    db.add(models.IngresoInventario(
        nombre_repuesto=item.nombre_insumo,
        cantidad=item.cantidad_disponible,
        fecha=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    
    db.commit()
    return {"mensaje": f"Ítem '{item.nombre_insumo}' creado exitosamente."}

@router.post("/{item_id}/abastecer")
def abastecer_item(item_id: int, cantidad: float, db: Session = Depends(get_db)):
    item = db.query(models.Inventario).filter(models.Inventario.id == item_id).first()
    if not item:
        return {"error": "Ítem no encontrado"}
    
    item.cantidad_disponible += cantidad
    
    nuevo_ingreso = models.IngresoInventario(
        nombre_repuesto=item.nombre_insumo,
        cantidad=cantidad,
        fecha=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    db.add(nuevo_ingreso)
    db.commit()
    return {"mensaje": f"Ingreso exitoso: Se sumaron {cantidad} a '{item.nombre_insumo}'."}

@router.get("/ingresos")
def obtener_historial_ingresos(db: Session = Depends(get_db)):
    return db.query(models.IngresoInventario).order_by(models.IngresoInventario.id.desc()).all()

@router.get("/movimientos")
def obtener_movimientos(db: Session = Depends(get_db)):
    movimientos = db.query(models.RepuestoUtilizado).order_by(models.RepuestoUtilizado.id.desc()).all()
    resultado = []
    
    for mov in movimientos:
        proceso = db.query(models.Proceso).filter(models.Proceso.id == mov.proceso_id).first()
        ods_texto = proceso.ods if proceso else f"ID-{mov.proceso_id}"
        
        cliente_texto = "Desconocido"
        if proceso:
            cliente = db.query(models.Cliente).filter(models.Cliente.id == proceso.id_cliente).first()
            if cliente:
                cliente_texto = cliente.razon_social
        
        resultado.append({
            "id": mov.id,
            "repuesto": mov.nombre_repuesto,
            "cantidad": mov.cantidad,
            "destino": mov.componente_destino,
            "ods": ods_texto,
            "cliente": cliente_texto
        })
    return resultado

@router.post("/salida-manual")
def registrar_salida_manual(nombre: str, cantidad: float, motivo: str, db: Session = Depends(get_db)):
    item = db.query(models.Inventario).filter(models.Inventario.nombre_insumo == nombre).first()
    if not item:
        return {"error": "El repuesto no existe en el inventario"}
    
    if item.cantidad_disponible < cantidad:
        return {"error": "Stock insuficiente"}
    
    item.cantidad_disponible -= cantidad
    
    nueva_salida = models.SalidaManual(
        nombre_repuesto=nombre,
        cantidad=cantidad,
        motivo=motivo,
        fecha=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    db.add(nueva_salida)
    db.commit()
    return {"mensaje": "Salida registrada correctamente"}

@router.get("/salidas-manuales")
def obtener_salidas_manuales(db: Session = Depends(get_db)):
    return db.query(models.SalidaManual).order_by(models.SalidaManual.id.desc()).all()