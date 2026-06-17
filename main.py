import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import database, models
import migrations
from routers import auth, clientes, inventario, operaciones, usuarios

models.Base.metadata.create_all(bind=database.engine)
migrations.ensure_schema()

app = FastAPI()
ANGULAR_DIST = Path(os.getenv("ANGULAR_DIST", "angular-dist"))

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
    return RedirectResponse(url="/login/")


@app.get("/login", include_in_schema=False)
async def redirigir_login():
    return RedirectResponse(url="/login/")


@app.get("/login/{asset_path:path}", include_in_schema=False)
async def mostrar_login_angular(asset_path: str):
    index_file = ANGULAR_DIST / "index.html"
    if not index_file.is_file():
        if asset_path:
            return HTMLResponse(content="<h1>Frontend Angular no compilado</h1>", status_code=404)
        return render_static_html("login.html", "login.html")

    dist_root = ANGULAR_DIST.resolve()
    requested = (ANGULAR_DIST / asset_path).resolve()
    if asset_path and requested.is_file() and dist_root in requested.parents:
        return FileResponse(requested)
    return FileResponse(index_file)


@app.get("/assets/{asset_path:path}", include_in_schema=False)
async def mostrar_asset_angular(asset_path: str):
    assets_root = (ANGULAR_DIST / "assets").resolve()
    requested = (assets_root / asset_path).resolve()
    if requested.is_file() and assets_root in requested.parents:
        return FileResponse(requested)
    return HTMLResponse(content="Asset no encontrado", status_code=404)


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
