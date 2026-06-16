import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import database, models
from routers import auth, clientes, inventario, operaciones, usuarios

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


def render_static_html(filename: str, error_label: str) -> HTMLResponse:
    try:
        with open(f"static/{filename}", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content=f"<h1>Error: {error_label} no encontrado</h1>", status_code=404)


@app.get("/")
async def raiz():
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
async def mostrar_login(request: Request):
    return render_static_html("login.html", "login.html")


@app.get("/operativo", response_class=HTMLResponse)
async def mostrar_operativo(request: Request):
    return render_static_html("index.html", "index.html")


@app.get("/admin", response_class=HTMLResponse)
async def mostrar_admin(request: Request):
    return render_static_html("admin.html", "admin.html")


app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(inventario.router)
app.include_router(operaciones.router)
app.include_router(usuarios.router)
