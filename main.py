import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import database, models
from routers import clientes, inventario, operaciones, usuarios

# Crea las tablas en PostgreSQL automáticamente al arrancar
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Le indicamos a FastAPI que configure la carpeta para soportar archivos estáticos
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def mostrar_portal(request: Request):
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: index.html no encontrado</h1>", status_code=404)

@app.get("/admin", response_class=HTMLResponse)
async def mostrar_admin(request: Request):
    try:
        with open("static/admin.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: admin.html no encontrado</h1>", status_code=404)

# ==========================================
# CONEXIÓN DE LOS MÓDULOS INDEPENDIENTES
# ==========================================
app.include_router(clientes.router)
app.include_router(inventario.router)
app.include_router(operaciones.router)
app.include_router(usuarios.router)  # <--- ESTE ES EL CABLE QUE NOS FALTABA