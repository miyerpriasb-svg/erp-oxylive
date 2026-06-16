from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import get_db

# Aquí creamos el "enchufe" para este módulo específico
router = APIRouter(
    prefix="/clientes",
    tags=["Módulo de Clientes"]
)

# El esquema de validación
class ClienteNuevo(BaseModel):
    razon_social: str
    nit: str

# Las rutas (nota que ahora usamos @router en lugar de @app y quitamos "/clientes" de la ruta porque ya está en el prefix)
@router.post("/")
def crear_cliente(cliente: ClienteNuevo, db: Session = Depends(get_db)):
    nuevo_cliente = models.Cliente(razon_social=cliente.razon_social, nit=cliente.nit)
    db.add(nuevo_cliente)
    db.commit()
    return {"mensaje": f"Cliente '{cliente.razon_social}' registrado exitosamente."}

@router.get("/")
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(models.Cliente).all()
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import get_db

router = APIRouter(
    prefix="/clientes",
    tags=["Módulo de Clientes"]
)

class ClienteNuevo(BaseModel):
    razon_social: str
    nit: str

@router.get("/")
def obtener_clientes(db: Session = Depends(get_db)):
    return db.query(models.Cliente).all()

@router.post("/")
def crear_cliente(cliente: ClienteNuevo, db: Session = Depends(get_db)):
    nuevo = models.Cliente(
        razon_social=cliente.razon_social, 
        nit=cliente.nit
    )
    db.add(nuevo)
    db.commit()
    return {"mensaje": f"Cliente {cliente.razon_social} registrado."}