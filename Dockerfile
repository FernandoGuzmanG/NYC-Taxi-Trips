# Usamos una imagen ligera de Python 3.11
FROM python:3.11-slim

# Evita que Python genere archivos .pyc y fuerza la salida de logs a la consola
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalamos dependencias del sistema necesarias para compilar psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copiamos e instalamos los requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# El código se montará como volumen, así que no necesitamos hacer COPY . . aquí
CMD ["bash"]