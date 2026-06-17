# ERP Oxylive Angular

Primera fase de la migracion del frontend. El login Angular consume el endpoint existente `POST /auth/login` y redirige al panel legado correspondiente mientras se migran los demas modulos.

## Ejecucion local

1. Instalar dependencias dentro de `frontend` con `npm install`.
2. Iniciar Angular con `npm start`.
3. Abrir `http://localhost:4200/`.

El proxy local envia `/auth`, `/admin`, `/operativo` y `/static` hacia el backend publicado en Render.

En produccion, FastAPI sirve Angular desde `/login/`. Los paneles `/admin` y `/operativo` permanecen en el frontend vigente mientras se completa la migracion.

## Estado de migracion

- Login y sesion: migrados.
- Redireccion por roles: conectada al backend actual.
- Guard de autenticacion: preparado.
- Panel administrativo: pendiente.
- Panel operativo: pendiente.
