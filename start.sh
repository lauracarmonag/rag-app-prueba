#!/bin/bash

# Iniciar Ollama en segundo plano
ollama serve &

# Esperar a que Ollama esté listo
echo "Esperando a que Ollama inicie..."
sleep 15

# Descargar el modelo mistral
echo "Descargando modelo mistral..."
ollama pull mistral

# Iniciar la aplicación Streamlit con el puerto correcto
echo "Iniciando Streamlit..."
exec streamlit run app.py --server.port="$PORT" --server.address="0.0.0.0"