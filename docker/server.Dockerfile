FROM python:3.9-alpine

RUN addgroup -S app && \
    adduser -h /opt/app -S app -G app 

ADD --chown=app:app . /opt/app

WORKDIR /opt/app

RUN apk add --no-cache --update-cache alpine-sdk

RUN pip3 --no-cache-dir install /opt/app -U

ENV PORT=8000

ENTRYPOINT [ "sh", "-c", "server --port $PORT" ]