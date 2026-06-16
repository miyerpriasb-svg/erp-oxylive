# Usar una imagen base de Python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias (asumiendo que tienes un archivo requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Comando para arrancar tu API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]