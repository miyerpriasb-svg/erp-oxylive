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

DEFAULT_CARGOS = {
    "GERENTE GENERAL": {"categoria": "ADMINISTRATIVO", "especialidades": []},
    "COORDINADOR ADMINISTRATIVO": {"categoria": "ADMINISTRATIVO", "especialidades": []},
    "COORDINADOR COMERCIAL": {"categoria": "ADMINISTRATIVO", "especialidades": []},
    "CONTADOR": {"categoria": "ADMINISTRATIVO", "especialidades": []},
    "JURIDICO": {"categoria": "ADMINISTRATIVO", "especialidades": []},
    "TECNICO DE ESTACIONARIOS": {"categoria": "TECNICO", "especialidades": ["ESTACIONARIOS"]},
    "TECNICO DE PORTATILES": {"categoria": "TECNICO", "especialidades": ["PORTATILES"]},
    "TECNICO DE LLENA": {"categoria": "TECNICO", "especialidades": ["TAMICES"]},
    "TECNICO DE COMPRESORES": {"categoria": "TECNICO", "especialidades": ["COMPRESORES"]},
}


class LoginData(BaseModel):
    usuario: str
    password: str


def roles_usuario(rol: str):
    return [r.strip().upper() for r in (rol or "").split(",") if r.strip()]


def mapa_cargos(db: Session):
    cargos = {nombre: data.copy() for nombre, data in DEFAULT_CARGOS.items()}
    try:
        for cargo in db.query(models.Cargo).all():
            especialidades = [
                item.strip().upper()
                for item in (cargo.especialidades or "").split(",")
                if item.strip()
            ]
            cargos[(cargo.nombre or "").strip().upper()] = {
                "categoria": (cargo.categoria or "ADMINISTRATIVO").strip().upper(),
                "especialidades": especialidades,
            }
    except Exception:
        pass
    return cargos


def validar_roles(rol: str, db: Session):
    roles = roles_usuario(rol)
    cargos = mapa_cargos(db)
    if not roles or any(r not in cargos for r in roles):
        raise HTTPException(status_code=403, detail="Cargo no habilitado")
    return roles


def categorias_por_roles(roles, db: Session):
    cargos = mapa_cargos(db)
    return {rol: cargos.get(rol, {}).get("categoria", "ADMINISTRATIVO") for rol in roles}


def especialidades_por_roles(roles, db: Session):
    cargos = mapa_cargos(db)
    return {rol: cargos.get(rol, {}).get("especialidades", []) for rol in roles}


def destino_por_roles(roles, db: Session) -> str:
    categorias = categorias_por_roles(roles, db)
    if any(categoria == "ADMINISTRATIVO" for categoria in categorias.values()):
        return "/admin"
    if any(categoria == "TECNICO" for categoria in categorias.values()):
        return "/operativo"
    raise HTTPException(status_code=403, detail="Cargo no habilitado")


@router.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    usuario = data.usuario.strip().lower()
    password = data.password

    user = db.query(models.Usuario).filter(models.Usuario.username == usuario).first()
    if user and (user.activo or "SI").upper() != "NO" and user.password == password:
        roles = validar_roles(user.rol or "", db)
        return {
            "id": user.id,
            "nombre": user.nombre,
            "usuario": user.username,
            "rol": ", ".join(roles),
            "roles": roles,
            "categorias": categorias_por_roles(roles, db),
            "especialidades": especialidades_por_roles(roles, db),
            "redirect": destino_por_roles(roles, db),
        }

    # Respaldo inicial para poder entrar y crear personal aunque la base tenga usuarios antiguos sin credenciales.
    if usuario in FALLBACK_USERS and password == DEFAULT_PASSWORD:
        session = FALLBACK_USERS[usuario].copy()
        roles = validar_roles(session["rol"], db)
        session["usuario"] = usuario
        session["roles"] = roles
        session["categorias"] = categorias_por_roles(roles, db)
        session["especialidades"] = especialidades_por_roles(roles, db)
        session["redirect"] = destino_por_roles(roles, db)
        return session

    raise HTTPException(status_code=401, detail="Usuario o contrasena incorrectos")
