FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

CMD ["sh", "-c", "exec uvicorn main:app --host ${UVICORN_HOST:-0.0.0.0} --port ${UVICORN_PORT:-8000} --timeout-keep-alive ${UVICORN_TIMEOUT_KEEP_ALIVE:-10}"]
