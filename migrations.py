from sqlalchemy import inspect, text
import database


def ensure_column(connection, table_name, column_name, column_type):
    inspector = inspect(connection)
    existing = {column["name"] for column in inspector.get_columns(table_name)}
    if column_name not in existing:
        connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))


def ensure_schema():
    with database.engine.begin() as connection:
        ensure_column(connection, "usuarios", "username", "VARCHAR")
        ensure_column(connection, "usuarios", "password", "VARCHAR")
        ensure_column(connection, "usuarios", "activo", "VARCHAR")
        ensure_column(connection, "clientes", "tipo_cliente", "VARCHAR")
        ensure_column(connection, "clientes", "correo", "VARCHAR")
        ensure_column(connection, "clientes", "telefono", "VARCHAR")
        ensure_column(connection, "procesos", "tipo_equipo", "VARCHAR")
        ensure_column(connection, "procesos", "marca_equipo", "VARCHAR")
        ensure_column(connection, "procesos", "modelo_equipo", "VARCHAR")
        ensure_column(connection, "procesos", "horas_ingreso", "FLOAT")
        ensure_column(connection, "procesos", "modalidad_servicio", "VARCHAR")
