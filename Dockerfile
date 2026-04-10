# 1. Imagen base
FROM python:3.9-slim

# 2. Directorio de trabajo
WORKDIR /app

# 3. Copiar dependencias e instalarlas
COPY requirements.txt .
RUN pip install -r requirements.txt

# 4. Copiar el resto del código
COPY . .

# 5. Puerto a exponer
EXPOSE 5000

# 6. Comando de inicio
CMD ["python", "app.py"]