from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Union
import models
from database import get_db

router = APIRouter(tags=["Modulo de Personal"])

ROLES_PERMITIDOS = {
    "GERENTE GENERAL",
    "COORDINADOR ADMINISTRATIVO",
    "COORDINADOR COMERCIAL",
    "CONTADOR",
    "JURIDICO",
    "TECNICO DE ESTACIONARIOS",
    "TECNICO DE PORTATILES",
    "TECNICO DE LLENA",
    "TECNICO DE COMPRESORES",
}


def normalizar_roles(roles: Union[str, List[str]]) -> str:
    if isinstance(roles, str):
        candidatos = [r.strip().upper() for r in roles.split(",")]
    else:
        candidatos = [str(r).strip().upper() for r in roles]
    roles_limpios = []
    for rol in candidatos:
        if not rol:
            continue
        if rol not in ROLES_PERMITIDOS:
            raise HTTPException(status_code=400, detail=f"Rol no permitido: {rol}")
        if rol not in roles_limpios:
            roles_limpios.append(rol)
    if not roles_limpios:
        raise HTTPException(status_code=400, detail="Debe asignar al menos un rol")
    return ", ".join(roles_limpios)


def roles_usuario(rol: str) -> List[str]:
    return [r.strip().upper() for r in (rol or "").split(",") if r.strip()]


class UsuarioNuevo(BaseModel):
    nombre: str
    username: str
    password: str
    rol: Union[str, List[str]]
    activo: Optional[str] = "SI"


class UsuarioActualizar(BaseModel):
    nombre: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    rol: Optional[Union[str, List[str]]] = None
    activo: Optional[str] = None


@router.get("/usuarios")
def obtener_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).order_by(models.Usuario.id.desc()).all()
    return [
        {
            "id": u.id,
            "nombre": u.nombre,
            "username": u.username,
            "rol": u.rol,
            "roles": roles_usuario(u.rol),
            "activo": u.activo or "SI",
        }
        for u in usuarios
    ]


@router.post("/usuarios")
def crear_usuario(user: UsuarioNuevo, db: Session = Depends(get_db)):
    username = user.username.strip().lower()
    rol = normalizar_roles(user.rol)
    if db.query(models.Usuario).filter(models.Usuario.username == username).first():
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    nuevo = models.Usuario(
        nombre=user.nombre,
        username=username,
        password=user.password,
        rol=rol,
        activo=user.activo or "SI",
    )
    db.add(nuevo)
    db.commit()
    return {"mensaje": f"Usuario {user.nombre} creado exitosamente."}


@router.put("/usuarios/{usuario_id}")
def actualizar_usuario(usuario_id: int, data: UsuarioActualizar, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if data.username:
        username = data.username.strip().lower()
        existe = db.query(models.Usuario).filter(
            models.Usuario.username == username,
            models.Usuario.id != usuario_id
        ).first()
        if existe:
            raise HTTPException(status_code=400, detail="El usuario ya existe")
        user.username = username

    if data.nombre is not None:
        user.nombre = data.nombre
    if data.password:
        user.password = data.password
    if data.rol:
        user.rol = normalizar_roles(data.rol)
    if data.activo:
        user.activo = data.activo

    db.commit()
    return {"mensaje": "Usuario actualizado"}


@router.post("/usuarios/{usuario_id}/estado")
def cambiar_estado_usuario(usuario_id: int, activo: str, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.activo = activo
    db.commit()
    return {"mensaje": "Estado actualizado"}
