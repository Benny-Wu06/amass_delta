FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY microservices/data_retrieval/src/ ./src/

ENV PYTHONPATH=/app/src

ENV TARGET_COMPANY="Microsoft"

EXPOSE 8000

# docker run -e TARGET_COMPANY="Apple" amass-retrieval to run other companies
CMD python -c "from company_vulnerabilities import lambda_handler; \
    event = {'pathParameters': {'company_name': '$TARGET_COMPANY'}}; \
    print(lambda_handler(event, None))"