FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY microservices/ ./microservices/

EXPOSE 8080

CMD ["python", "microservices/data_collection/src/cisa.py"]