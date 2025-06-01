FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg git curl build-essential cmake \
    libopenblas-dev libomp-dev ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Installer Poetry
RUN pip install --no-cache-dir poetry

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du projet
COPY . /app

# Installer les dépendances du projet
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Définir la commande de démarrage
CMD ["python3", "serverless_main.py"]
