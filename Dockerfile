FROM runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04

# Éviter les invites interactives
ENV DEBIAN_FRONTEND=noninteractive

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-dev python3-distutils python3-pip \
    git ffmpeg wget curl build-essential cmake \
    libopenblas-dev libomp-dev ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Ajouter un alias python3.10 -> python
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Installer pip si besoin
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3

# Copier les fichiers du projet (adapte si besoin)
COPY . /app
WORKDIR /app

# Installer les dépendances Python (si tu as requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]
