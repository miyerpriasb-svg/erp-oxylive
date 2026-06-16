from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import get_db

router = APIRouter(prefix="/auth", tags=["Acceso"])

DEFAULT_PASSWORD = "admin123"

FALLBACK_USERS = {
    "administrador": {"id": 0, "nombre": "Gerente General Oxylive", "rol": "GERENTE GENERAL"},
}

ROLES_ADMIN = {
    "GERENTE GENERAL",
    "COORDINADOR ADMINISTRATIVO",
    "COORDINADOR COMERCIAL",
    "CONTADOR",
    "JURIDICO",
}
ROLES_TECNICOS = {
    "TECNICO DE ESTACIONARIOS",
    "TECNICO DE PORTATILES",
    "TECNICO DE LLENA",
    "TECNICO DE COMPRESORES",
}
ROLES_PERMITIDOS = ROLES_ADMIN | ROLES_TECNICOS


class LoginData(BaseModel):
    usuario: str
    password: str


def roles_usuario(rol: str):
    return [r.strip().upper() for r in (rol or "").split(",") if r.strip()]


def validar_roles(rol: str):
    roles = roles_usuario(rol)
    if not roles or any(r not in ROLES_PERMITIDOS for r in roles):
        raise HTTPException(status_code=403, detail="Rol no habilitado")
    return roles


def destino_por_roles(roles) -> str:
    if any(r in ROLES_ADMIN for r in roles):
        return "/admin"
    if any(r in ROLES_TECNICOS for r in roles):
        return "/operativo"
    raise HTTPException(status_code=403, detail="Rol no habilitado")


@router.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    usuario = data.usuario.strip().lower()
    password = data.password

    user = db.query(models.Usuario).filter(models.Usuario.username == usuario).first()
    if user and (user.activo or "SI").upper() != "NO" and user.password == password:
        roles = validar_roles(user.rol or "")
        return {
            "id": user.id,
            "nombre": user.nombre,
            "usuario": user.username,
            "rol": ", ".join(roles),
            "roles": roles,
            "redirect": destino_por_roles(roles),
        }

    # Respaldo inicial para poder entrar y crear personal aunque la base tenga usuarios antiguos sin credenciales.
    if usuario in FALLBACK_USERS and password == DEFAULT_PASSWORD:
        session = FALLBACK_USERS[usuario].copy()
        roles = validar_roles(session["rol"])
        session["usuario"] = usuario
        session["roles"] = roles
        session["redirect"] = destino_por_roles(roles)
        return session

    raise HTTPException(status_code=401, detail="Usuario o contrasena incorrectos")
