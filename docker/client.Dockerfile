FROM python:3.9-alpine

RUN addgroup -S app && \
    adduser -h /opt/app -S app -G app 

ADD --chown=app:app . /opt/app

WORKDIR /opt/app

RUN apk add --no-cache --update-cache alpine-sdk

RUN pip3 --no-cache-dir install /opt/app -U

ENV NAME=client
ENV PORT=8001
ENV SERVER_IP=localhost
ENV SERVER_PORT=8000

ENTRYPOINT [ "sh", "-c", "client --name $NAME --port $PORT --server-ip $SERVER_IP --server-port $SERVER_PORT" ]