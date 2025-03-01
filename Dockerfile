FROM python:3.13.2-bookworm

RUN set -ex
USER root

COPY . /app
WORKDIR /app

CMD ["python3", "-m", "src.main"]