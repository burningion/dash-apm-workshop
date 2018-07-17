FROM python:3.6.2-alpine3.6
LABEL maintainer="Datadog Inc. <manu@datadoghq.com>"

RUN apk update \
    apk add curl
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
