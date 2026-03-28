FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY microservices/data_collection/src/ ./src/

ENV PYTHONPATH=/app/src

CMD python -c "from cisascrapper import cisascrapper; cisascrapper({}, None)" && \
    python -c "from nvdscrapper import nvdscrapper; nvdscrapper({}, None)" && \
    python -c "from enrichment import enrichment; enrichment({}, None)" && \
    python -c "from processor import lambda_handler; lambda_handler({}, None)"