FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema para Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY backend/requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY backend/ .
COPY frontend/ ../frontend/

# Exponer puerto
EXPOSE 8000

# Comando para iniciar
CMD ["python", "main.py"]
