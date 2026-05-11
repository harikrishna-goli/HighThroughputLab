FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

CMD ["sh", "-c", "gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers ${WEB_CONCURRENCY:-3} --worker-connections ${WORKER_CONNECTIONS:-1000} --max-requests 10000 --max-requests-jitter 1000 --timeout 30 --keep-alive 5"]
