FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install -r ./requirements.txt

CMD ["python", "-c", "from src.cisa import cisascrapper; cisascrapper({}, None)"]