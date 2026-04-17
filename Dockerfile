FROM python:3.11-slim

WORKDIR /app

COPY requirements-dev.txt /app/requirements-dev.txt
RUN python -m pip install --upgrade pip && \
    python -m pip install -r /app/requirements-dev.txt

COPY . /app

ENV PYTHONPATH=src
ENV APP_MODE=dev
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000
ENV LOG_LEVEL=info
ENV APP_MODULE=server.fastapi_app:app
ENV APP_RELOAD=false
ENV WEBHOOK_BASE_PATH=/webhooks

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "server.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
