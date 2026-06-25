from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Union
import models
from database import get_db

router = APIRouter(tags=["Modulo de Personal"])

CATEGORIAS_CARGO = {"ADMINISTRATIVO", "TECNICO"}
CARGO_PROTEGIDO = "GERENTE GENERAL"

DEFAULT_CARGOS = [
    ("GERENTE GENERAL", "ADMINISTRATIVO"),
    ("COORDINADOR ADMINISTRATIVO", "ADMINISTRATIVO"),
    ("COORDINADOR COMERCIAL", "ADMINISTRATIVO"),
    ("CONTADOR", "ADMINISTRATIVO"),
    ("JURIDICO", "ADMINISTRATIVO"),
    ("TECNICO DE ESTACIONARIOS", "TECNICO"),
    ("TECNICO DE PORTATILES", "TECNICO"),
    ("TECNICO DE LLENA", "TECNICO"),
    ("TECNICO DE COMPRESORES", "TECNICO"),
]
CARGOS_BASE_PROTEGIDOS = {nombre for nombre, _ in DEFAULT_CARGOS}


def normalizar_cargo(nombre: str) -> str:
    return " ".join(str(nombre or "").strip().upper().split())


def normalizar_categoria(categoria: str) -> str:
    categoria_limpia = normalizar_cargo(categoria)
    if categoria_limpia not in CATEGORIAS_CARGO:
        raise HTTPException(status_code=400, detail="La categoria debe ser ADMINISTRATIVO o TECNICO")
    return categoria_limpia


def asegurar_cargos_base(db: Session):
    existentes = {normalizar_cargo(c.nombre) for c in db.query(models.Cargo).all()}
    for nombre, categoria in DEFAULT_CARGOS:
        if nombre not in existentes:
            db.add(models.Cargo(nombre=nombre, categoria=categoria))
    db.commit()


def obtener_cargos(db: Session) -> List[models.Cargo]:
    asegurar_cargos_base(db)
    return db.query(models.Cargo).order_by(models.Cargo.categoria, models.Cargo.nombre).all()


def normalizar_roles(roles: Union[str, List[str]], db: Session) -> str:
    if isinstance(roles, str):
        candidatos = [r.strip().upper() for r in roles.split(",")]
    else:
        candidatos = [str(r).strip().upper() for r in roles]
    roles_permitidos = {normalizar_cargo(c.nombre) for c in obtener_cargos(db)}
    roles_limpios = []
    for rol in candidatos:
        rol = normalizar_cargo(rol)
        if not rol:
            continue
        if rol not in roles_permitidos:
            raise HTTPException(status_code=400, detail=f"Cargo no permitido: {rol}")
        if rol not in roles_limpios:
            roles_limpios.append(rol)
    if not roles_limpios:
        raise HTTPException(status_code=400, detail="Debe asignar al menos un cargo")
    if len(roles_limpios) > 2:
        raise HTTPException(status_code=400, detail="Un empleado solo puede tener uno o dos cargos")
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


class CargoNuevo(BaseModel):
    nombre: str
    categoria: str = "ADMINISTRATIVO"


@router.get("/usuarios/cargos")
def listar_cargos(db: Session = Depends(get_db)):
    return [
        {
            "id": cargo.id,
            "nombre": cargo.nombre,
            "categoria": cargo.categoria or "ADMINISTRATIVO",
            "protegido": normalizar_cargo(cargo.nombre) in CARGOS_BASE_PROTEGIDOS,
        }
        for cargo in obtener_cargos(db)
    ]


@router.post("/usuarios/cargos")
def crear_cargo(cargo: CargoNuevo, db: Session = Depends(get_db)):
    nombre = normalizar_cargo(cargo.nombre)
    categoria = normalizar_categoria(cargo.categoria)
    if not nombre:
        raise HTTPException(status_code=400, detail="El nombre del cargo es obligatorio")
    if db.query(models.Cargo).filter(models.Cargo.nombre == nombre).first():
        raise HTTPException(status_code=400, detail="El cargo ya existe")
    nuevo = models.Cargo(nombre=nombre, categoria=categoria)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"id": nuevo.id, "nombre": nuevo.nombre, "categoria": nuevo.categoria}


@router.delete("/usuarios/cargos/{cargo_id}")
def eliminar_cargo(cargo_id: int, db: Session = Depends(get_db)):
    cargo = db.query(models.Cargo).filter(models.Cargo.id == cargo_id).first()
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo no encontrado")
    nombre = normalizar_cargo(cargo.nombre)
    if nombre in CARGOS_BASE_PROTEGIDOS:
        raise HTTPException(status_code=400, detail="Los cargos base del sistema no se pueden eliminar")
    usuarios = db.query(models.Usuario).all()
    if any(nombre in roles_usuario(usuario.rol) for usuario in usuarios):
        raise HTTPException(status_code=400, detail="No se puede eliminar un cargo asignado a empleados")
    db.delete(cargo)
    db.commit()
    return {"mensaje": "Cargo eliminado"}


@router.get("/usuarios")
def obtener_usuarios(db: Session = Depends(get_db)):
    cargos = {normalizar_cargo(c.nombre): c.categoria for c in obtener_cargos(db)}
    usuarios = db.query(models.Usuario).order_by(models.Usuario.id.desc()).all()
    return [
        {
            "id": u.id,
            "nombre": u.nombre,
            "username": u.username,
            "rol": u.rol,
            "roles": roles_usuario(u.rol),
            "categorias": {rol: cargos.get(rol, "ADMINISTRATIVO") for rol in roles_usuario(u.rol)},
            "activo": u.activo or "SI",
        }
        for u in usuarios
    ]


@router.post("/usuarios")
def crear_usuario(user: UsuarioNuevo, db: Session = Depends(get_db)):
    username = user.username.strip().lower()
    rol = normalizar_roles(user.rol, db)
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
        user.rol = normalizar_roles(data.rol, db)
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
