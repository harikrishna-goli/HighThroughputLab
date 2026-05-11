FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

CMD ["sh", "-c", "gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers ${WEB_CONCURRENCY:-3} --worker-connections ${WORKER_CONNECTIONS:-1000} --max-requests ${MAX_REQUESTS:-10000} --max-requests-jitter ${MAX_REQUESTS_JITTER:-1000} --timeout ${GUNICORN_TIMEOUT:-30} --keep-alive ${GUNICORN_KEEP_ALIVE:-5}"]
