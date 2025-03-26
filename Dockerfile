FROM python:3.13.2-bookworm

RUN set -ex
USER root

COPY . /app
WORKDIR /app
RUN pip install -r src/requirements.txt

ARG BOT_TOKEN
ENV BOT_TOKEN=$BOT_TOKEN

RUN echo "Token: $BOT_TOKEN"

CMD ["python3", "-m", "src.main"]
