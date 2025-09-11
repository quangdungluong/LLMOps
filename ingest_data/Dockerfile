FROM apache/airflow:2.9.0

USER root

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt /app/requirements.txt

RUN pip install apache-airflow==2.9.0 -r /app/requirements.txt

