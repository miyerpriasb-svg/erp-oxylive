from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import models
from database import get_db

router = APIRouter(tags=["Modulo de Personal"])


class UsuarioNuevo(BaseModel):
    nombre: str
    username: str
    password: str
    rol: str
    activo: Optional[str] = "SI"


@router.get("/usuarios")
def obtener_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).order_by(models.Usuario.id.desc()).all()
    return [
        {
            "id": u.id,
            "nombre": u.nombre,
            "username": u.username,
            "rol": u.rol,
            "activo": u.activo or "SI",
        }
        for u in usuarios
    ]


@router.post("/usuarios")
def crear_usuario(user: UsuarioNuevo, db: Session = Depends(get_db)):
    username = user.username.strip().lower()
    if db.query(models.Usuario).filter(models.Usuario.username == username).first():
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    nuevo = models.Usuario(
        nombre=user.nombre,
        username=username,
        password=user.password,
        rol=user.rol,
        activo=user.activo or "SI",
    )
    db.add(nuevo)
    db.commit()
    return {"mensaje": f"Usuario {user.nombre} creado exitosamente."}
