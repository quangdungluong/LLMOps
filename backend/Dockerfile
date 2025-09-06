FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install --no-install-recommends -y g++ gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY requirements.txt .

RUN uv pip install --system --no-cache-dir -r requirements.txt

COPY . .
