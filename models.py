from sqlalchemy import Column, Integer, String, Float
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    username = Column(String, index=True)
    password = Column(String)
    rol = Column(String)
    activo = Column(String, default="SI")

class Cargo(Base):
    __tablename__ = "cargos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    categoria = Column(String, default="ADMINISTRATIVO")
    especialidades = Column(String, default="")

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    razon_social = Column(String, index=True)
    nit = Column(String, index=True)
    tipo_cliente = Column(String)
    correo = Column(String)
    telefono = Column(String)

class Inventario(Base):
    __tablename__ = "inventario"
    id = Column(Integer, primary_key=True, index=True)
    nombre_insumo = Column(String, index=True)
    cantidad_disponible = Column(Float)
    unidad_medida = Column(String)
    stock_minimo_alerta = Column(Float)

class Proceso(Base):
    __tablename__ = "procesos"
    id = Column(Integer, primary_key=True, index=True)
    ods = Column(String, index=True)
    tipo_tarea = Column(String)
    tipo_equipo = Column(String)
    marca_equipo = Column(String)
    modelo_equipo = Column(String)
    horas_ingreso = Column(Float)
    modalidad_servicio = Column(String)
    parent_proceso_id = Column(Integer)
    sub_ods_tipo = Column(String)
    id_cliente = Column(Integer)
    id_trabajador_asignado = Column(Integer)
    estado = Column(String)
    porcentaje_avance = Column(Integer)
    # NUEVAS COLUMNAS DE TIEMPO
    fecha_creacion = Column(String)
    fecha_diagnostico = Column(String)
    fecha_aprobacion = Column(String)
    fecha_finalizacion = Column(String)

class TamizOrden(Base):
    __tablename__ = "tamices_orden"
    id = Column(Integer, primary_key=True, index=True)
    proceso_id = Column(Integer, index=True)
    marca = Column(String)
    cantidad = Column(Float)
    unidad_conteo = Column(String)

class ReporteTecnico(Base):
    __tablename__ = "reportes_tecnicos"
    id = Column(Integer, primary_key=True, index=True)
    proceso_id = Column(Integer)
    ods_relacionada = Column(String)
    estado_compresor = Column(String)
    estado_electrovalvulas = Column(String)
    estado_tamiz = Column(String)
    observaciones = Column(String)
    recibido_por = Column(String)
    fecha = Column(String)

class RepuestoUtilizado(Base):
    __tablename__ = "repuestos_utilizados"
    id = Column(Integer, primary_key=True, index=True)
    proceso_id = Column(Integer)
    nombre_repuesto = Column(String)
    cantidad = Column(Float)
    componente_destino = Column(String)

class IngresoInventario(Base):
    __tablename__ = "ingresos_inventario"
    id = Column(Integer, primary_key=True, index=True)
    nombre_repuesto = Column(String)
    cantidad = Column(Float)
    fecha = Column(String)

class SalidaManual(Base):
    __tablename__ = "salidas_manuales"
    id = Column(Integer, primary_key=True, index=True)
    nombre_repuesto = Column(String)
    cantidad = Column(Float)
    motivo = Column(String)
    fecha = Column(String)

class Diagnostico(Base):
    __tablename__ = "diagnosticos"
    id = Column(Integer, primary_key=True, index=True)
    proceso_id = Column(Integer, index=True)
    tipo_equipo = Column(String) 
    estado_compresor = Column(String)
    estado_tamiz = Column(String)
    estado_valvulas = Column(String)
    estado_bateria = Column(String)
    observaciones = Column(String)

class InteraccionCliente(Base):
    __tablename__ = "interacciones_clientes"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, index=True)
    tipo = Column(String, index=True)
    detalle = Column(String)
    fecha = Column(String)
