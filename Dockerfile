FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Actualiza el sistema e instala las dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia el archivo de requerimientos para instalar dependencias de Python
COPY requirements.txt /app/

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente al contenedor
COPY web /app

# Expone el puerto 8501, usado por Streamlit
EXPOSE 80

# Configura el healthcheck para verificar que Streamlit esté funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Define el comando de inicio del contenedor
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=80", "--server.address=0.0.0.0"]
