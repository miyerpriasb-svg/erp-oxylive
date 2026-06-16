from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import get_db

router = APIRouter(tags=["Módulo de Equipo"])

class UsuarioNuevo(BaseModel):
    nombre: str
    rol: str

@router.get("/usuarios")
def obtener_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()

@router.post("/usuarios")
def crear_usuario(user: UsuarioNuevo, db: Session = Depends(get_db)):
    nuevo = models.Usuario(
        nombre=user.nombre, 
        rol=user.rol
    )
    db.add(nuevo)
    db.commit()
    return {"mensaje": f"Usuario {user.nombre} creado exitosamente."}