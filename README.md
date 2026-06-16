# ERP Oxylive Service LLC

Aplicativo web para conectar la administración en Bogotá con la operación de campo y taller de Oxylive Service LLC.

## Módulos incluidos

- Seguridad y control de accesos por rol.
- Gestión de órdenes de servicio (ODS).
- Inventario, kardex y alertas de stock crítico.
- Directorio de clientes y usuarios internos.

## Estructura actual

El proyecto contiene una base backend con FastAPI y PostgreSQL:

- `main.py`: entrada de la API y servidor de páginas.
- `models.py`: modelos de base de datos.
- `database.py`: conexión SQLAlchemy.
- `routers/`: rutas de clientes, usuarios, inventario y operaciones.
- `static/`: pantallas conectadas al backend.
- `docker-compose.yml`: servicios de API, PostgreSQL y Redis.

También se conserva un prototipo estático en la raíz:

- `login.html`
- `admin.html`
- `index.html`
- `app.js`
- `styles.css`

## Uso con Docker

Con Docker Desktop instalado:

```powershell
docker compose up --build
```

Luego abre:

```text
http://localhost:3000/
http://localhost:3000/admin
```

## Uso del prototipo estático

Abre `login.html` en el navegador.

Usuarios de prueba:

| Usuario | Contraseña | Rol |
| --- | --- | --- |
| `admin` | `oxylive123` | Administrador |
| `coordinador` | `oxylive123` | Coordinador |
| `recepcion` | `oxylive123` | Recepcionista |
| `campo` | `oxylive123` | Técnico de campo |
| `taller` | `oxylive123` | Técnico de taller |

Los datos se guardan en el almacenamiento local del navegador para facilitar pruebas sin servidor.

## Conexión con GitHub

El repositorio remoto previsto es:

```text
https://github.com/miyerpriasb-svg/erp-oxylive.git
```

Si Git está instalado, ejecuta:

```powershell
.\conectar-github.ps1
```
