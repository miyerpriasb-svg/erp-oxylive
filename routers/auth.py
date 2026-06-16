from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import models
from database import get_db

router = APIRouter(prefix="/auth", tags=["Acceso"])

DEFAULT_PASSWORD = "oxylive123"

ADMIN_USERS = {
    "admin": {"id": 0, "nombre": "Administrador Oxylive", "rol": "ADMINISTRADOR"},
    "coordinador": {"id": 0, "nombre": "Coordinador Oxylive", "rol": "COORDINADOR"},
    "recepcion": {"id": 0, "nombre": "Recepcion Oxylive", "rol": "RECEPCIONISTA"},
}


class LoginData(BaseModel):
    usuario: str
    password: str


def destino_por_rol(rol: str) -> str:
    rol_normalizado = (rol or "").upper()
    if rol_normalizado in {"TECNICO", "TRABAJADOR", "TECNICO CAMPO", "TECNICO TALLER"}:
        return "/operativo"
    return "/admin"


@router.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    usuario = data.usuario.strip().lower()
    password = data.password

    if usuario in ADMIN_USERS and password == DEFAULT_PASSWORD:
        session = ADMIN_USERS[usuario].copy()
        session["redirect"] = destino_por_rol(session["rol"])
        return session

    usuarios = db.query(models.Usuario).all()
    for user in usuarios:
        nombre_login = (user.nombre or "").strip().lower().replace(" ", "")
        if usuario in {nombre_login, str(user.id)} and password == DEFAULT_PASSWORD:
            return {
                "id": user.id,
                "nombre": user.nombre,
                "rol": user.rol,
                "redirect": destino_por_rol(user.rol),
            }

    raise HTTPException(status_code=401, detail="Usuario o contrasena incorrectos")
