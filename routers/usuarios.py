from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Union
import models
from database import get_db

router = APIRouter(tags=["Modulo de Personal"])

CATEGORIAS_CARGO = {"ADMINISTRATIVO", "TECNICO"}
ESPECIALIDADES_CARGO = {"ESTACIONARIOS", "PORTATILES", "TAMICES", "COMPRESORES"}
CARGO_PROTEGIDO = "GERENTE GENERAL"

DEFAULT_CARGOS = [
    ("GERENTE GENERAL", "ADMINISTRATIVO", ""),
    ("COORDINADOR ADMINISTRATIVO", "ADMINISTRATIVO", ""),
    ("COORDINADOR COMERCIAL", "ADMINISTRATIVO", ""),
    ("CONTADOR", "ADMINISTRATIVO", ""),
    ("JURIDICO", "ADMINISTRATIVO", ""),
    ("TECNICO DE ESTACIONARIOS", "TECNICO", "ESTACIONARIOS"),
    ("TECNICO DE PORTATILES", "TECNICO", "PORTATILES"),
    ("TECNICO DE LLENA", "TECNICO", "TAMICES"),
    ("TECNICO DE COMPRESORES", "TECNICO", "COMPRESORES"),
]
CARGOS_BASE_PROTEGIDOS = {nombre for nombre, _, _ in DEFAULT_CARGOS}


def normalizar_cargo(nombre: str) -> str:
    return " ".join(str(nombre or "").strip().upper().split())


def normalizar_categoria(categoria: str) -> str:
    categoria_limpia = normalizar_cargo(categoria)
    if categoria_limpia not in CATEGORIAS_CARGO:
        raise HTTPException(status_code=400, detail="La categoria debe ser ADMINISTRATIVO o TECNICO")
    return categoria_limpia


def lista_especialidades(valor: Union[str, List[str], None]) -> List[str]:
    if valor is None:
        candidatos = []
    elif isinstance(valor, str):
        candidatos = [item.strip().upper() for item in valor.split(",")]
    else:
        candidatos = [str(item).strip().upper() for item in valor]
    limpias = []
    for item in candidatos:
        item = normalizar_cargo(item)
        if not item:
            continue
        if item not in ESPECIALIDADES_CARGO:
            raise HTTPException(status_code=400, detail=f"Compatibilidad no permitida: {item}")
        if item not in limpias:
            limpias.append(item)
    return limpias


def texto_especialidades(valor: Union[str, List[str], None]) -> str:
    return ", ".join(lista_especialidades(valor))


def asegurar_cargos_base(db: Session):
    existentes = {normalizar_cargo(c.nombre) for c in db.query(models.Cargo).all()}
    for nombre, categoria, especialidades in DEFAULT_CARGOS:
        if nombre not in existentes:
            db.add(models.Cargo(nombre=nombre, categoria=categoria, especialidades=especialidades))
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
    especialidades: Optional[Union[str, List[str]]] = None


class CargoActualizar(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    especialidades: Optional[Union[str, List[str]]] = None


def cargo_en_uso(db: Session, nombre: str) -> bool:
    cargo = normalizar_cargo(nombre)
    return any(cargo in roles_usuario(usuario.rol) for usuario in db.query(models.Usuario).all())


@router.get("/usuarios/cargos")
def listar_cargos(db: Session = Depends(get_db)):
    return [
        {
            "id": cargo.id,
            "nombre": cargo.nombre,
            "categoria": cargo.categoria or "ADMINISTRATIVO",
            "especialidades": lista_especialidades(cargo.especialidades),
            "protegido": normalizar_cargo(cargo.nombre) in CARGOS_BASE_PROTEGIDOS,
        }
        for cargo in obtener_cargos(db)
    ]


@router.post("/usuarios/cargos")
def crear_cargo(cargo: CargoNuevo, db: Session = Depends(get_db)):
    nombre = normalizar_cargo(cargo.nombre)
    categoria = normalizar_categoria(cargo.categoria)
    especialidades = texto_especialidades(cargo.especialidades)
    if not nombre:
        raise HTTPException(status_code=400, detail="El nombre del cargo es obligatorio")
    if db.query(models.Cargo).filter(models.Cargo.nombre == nombre).first():
        raise HTTPException(status_code=400, detail="El cargo ya existe")
    nuevo = models.Cargo(nombre=nombre, categoria=categoria, especialidades=especialidades)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {
        "id": nuevo.id,
        "nombre": nuevo.nombre,
        "categoria": nuevo.categoria,
        "especialidades": lista_especialidades(nuevo.especialidades),
    }


@router.put("/usuarios/cargos/{cargo_id}")
def actualizar_cargo(cargo_id: int, data: CargoActualizar, db: Session = Depends(get_db)):
    cargo = db.query(models.Cargo).filter(models.Cargo.id == cargo_id).first()
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo no encontrado")

    nombre_actual = normalizar_cargo(cargo.nombre)
    nombre_nuevo = normalizar_cargo(data.nombre) if data.nombre is not None else nombre_actual
    if not nombre_nuevo:
        raise HTTPException(status_code=400, detail="El nombre del cargo es obligatorio")
    if nombre_nuevo != nombre_actual:
        if nombre_actual in CARGOS_BASE_PROTEGIDOS:
            raise HTTPException(status_code=400, detail="Los cargos base del sistema no se pueden renombrar")
        if cargo_en_uso(db, nombre_actual):
            raise HTTPException(status_code=400, detail="No se puede renombrar un cargo asignado a empleados")
        if db.query(models.Cargo).filter(models.Cargo.nombre == nombre_nuevo, models.Cargo.id != cargo_id).first():
            raise HTTPException(status_code=400, detail="El cargo ya existe")
        cargo.nombre = nombre_nuevo

    if data.categoria is not None:
        cargo.categoria = normalizar_categoria(data.categoria)
    if data.especialidades is not None:
        cargo.especialidades = texto_especialidades(data.especialidades)

    db.commit()
    db.refresh(cargo)
    return {
        "id": cargo.id,
        "nombre": cargo.nombre,
        "categoria": cargo.categoria,
        "especialidades": lista_especialidades(cargo.especialidades),
    }


@router.delete("/usuarios/cargos/{cargo_id}")
def eliminar_cargo(cargo_id: int, db: Session = Depends(get_db)):
    cargo = db.query(models.Cargo).filter(models.Cargo.id == cargo_id).first()
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo no encontrado")
    nombre = normalizar_cargo(cargo.nombre)
    if nombre in CARGOS_BASE_PROTEGIDOS:
        raise HTTPException(status_code=400, detail="Los cargos base del sistema no se pueden eliminar")
    if cargo_en_uso(db, nombre):
        raise HTTPException(status_code=400, detail="No se puede eliminar un cargo asignado a empleados")
    db.delete(cargo)
    db.commit()
    return {"mensaje": "Cargo eliminado"}


@router.get("/usuarios")
def obtener_usuarios(db: Session = Depends(get_db)):
    cargos = {
        normalizar_cargo(c.nombre): {
            "categoria": c.categoria or "ADMINISTRATIVO",
            "especialidades": lista_especialidades(c.especialidades),
        }
        for c in obtener_cargos(db)
    }
    usuarios = db.query(models.Usuario).order_by(models.Usuario.id.desc()).all()
    return [
        {
            "id": u.id,
            "nombre": u.nombre,
            "username": u.username,
            "rol": u.rol,
            "roles": roles_usuario(u.rol),
            "categorias": {rol: cargos.get(rol, {}).get("categoria", "ADMINISTRATIVO") for rol in roles_usuario(u.rol)},
            "especialidades": {
                rol: cargos.get(rol, {}).get("especialidades", [])
                for rol in roles_usuario(u.rol)
            },
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
