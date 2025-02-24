FROM ubuntu:22.04

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    curl \
    software-properties-common

# Instalar Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Configurar el directorio de trabajo
WORKDIR /app

# Copiar archivos de la aplicación
COPY requirements.txt .
COPY app.py .

# Instalar dependencias de Python
RUN pip3 install -r requirements.txt

# Script de inicio
COPY start.sh .
RUN chmod +x start.sh

# Variables de entorno
ENV PORT=8080

# Comando para ejecutar
ENTRYPOINT ["./start.sh"]