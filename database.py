from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Tomamos la URL de la base de datos que configuramos en el archivo de Docker
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/erp_db")

# Creamos el motor de conexión
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Esta "Base" es la que usaremos para crear nuestras tablas más adelante
Base = declarative_base()
# Agrega esto al final de database.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()