FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN --mount=type=cache,id=custom-pip,target=/root/.cache/pip pip install -r /app/requirements.txt

RUN mv /app/deploy/entrypoint /
RUN chmod +x /entrypoint

RUN mv /app/deploy/celery /
RUN chmod +x /celery

RUN mv /app/deploy/celery-beat /
RUN chmod +x /celery-beat

RUN mv /app/deploy/flower /
RUN chmod +x /flower



CMD ["./entrypoint"]