FROM python:3.13.2-bookworm

RUN set -ex
USER root

COPY . /app
WORKDIR /app
RUN pip install -r src/requirements.txt

CMD ["python3", "-m", "src.main"]
