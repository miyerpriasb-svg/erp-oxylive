import database
import models

def poblar_datos_prueba():
    db = database.SessionLocal()
    try:
        # Crear Cliente
        if db.query(models.Cliente).count() == 0:
            cliente = models.Cliente(razon_social="Clínica del Norte", nit="900123456-1")
            db.add(cliente)
            
        # Crear Usuario (Técnico)
        if db.query(models.Usuario).count() == 0:
            usuario = models.Usuario(nombre="Carlos (Técnico)", rol="TRABAJADOR")
            db.add(usuario)
            
        db.commit()

        # Crear Proceso (Asignando el cliente y usuario recién creados)
        cliente_db = db.query(models.Cliente).first()
        usuario_db = db.query(models.Usuario).first()

        if db.query(models.Proceso).count() == 0:
            proceso = models.Proceso(
                tipo_tarea="Mantenimiento compresor", 
                estado="PENDIENTE",
                porcentaje_avance=0,
                id_cliente=cliente_db.id,
                id_trabajador_asignado=usuario_db.id
            )
            db.add(proceso)
            db.commit()
            print("✅ Datos de prueba creados exitosamente (Cliente, Usuario y Proceso 1).")
        else:
            print("ℹ️ Los datos de prueba ya existían.")
            
    finally:
        db.close()

if __name__ == "__main__":
    print("Iniciando inyección de datos...")
    poblar_datos_prueba()