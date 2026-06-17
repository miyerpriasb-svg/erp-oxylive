FROM node:22-alpine AS angular-build

WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build:production


FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=angular-build /frontend/dist/erp-oxylive/browser ./angular-dist

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-3000}"]
