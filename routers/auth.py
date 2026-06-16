from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import get_db

router = APIRouter(prefix="/auth", tags=["Acceso"])

DEFAULT_PASSWORD = "admin123"

FALLBACK_USERS = {
    "administrador": {"id": 0, "nombre": "Administrador Oxylive", "rol": "ADMINISTRADOR"},
}


class LoginData(BaseModel):
    usuario: str
    password: str


def destino_por_rol(rol: str) -> str:
    rol_normalizado = (rol or "").upper()
    if rol_normalizado in {"OPERATIVO", "TECNICO", "TRABAJADOR", "TECNICO CAMPO", "TECNICO TALLER"}:
        return "/operativo"
    return "/admin"


@router.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    usuario = data.usuario.strip().lower()
    password = data.password

    user = db.query(models.Usuario).filter(models.Usuario.username == usuario).first()
    if user and (user.activo or "SI").upper() != "NO" and user.password == password:
        return {
            "id": user.id,
            "nombre": user.nombre,
            "usuario": user.username,
            "rol": user.rol,
            "redirect": destino_por_rol(user.rol),
        }

    # Respaldo inicial para poder entrar y crear personal aunque la base tenga usuarios antiguos sin credenciales.
    if usuario in FALLBACK_USERS and password == DEFAULT_PASSWORD:
        session = FALLBACK_USERS[usuario].copy()
        session["usuario"] = usuario
        session["redirect"] = destino_por_rol(session["rol"])
        return session

    raise HTTPException(status_code=401, detail="Usuario o contrasena incorrectos")
