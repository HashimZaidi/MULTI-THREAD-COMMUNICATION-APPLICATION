FROM python:3.9-alpine

RUN apk add --no-cache --update-cache alpine-sdk

RUN addgroup -S app && \
    adduser -h /opt/app -S app -G app 

ADD --chown=app:app . /opt/app

WORKDIR /opt/app

RUN pip3 --no-cache-dir install /opt/app -U

RUN chmod +x /opt/app/docker/docker-entrypoint.sh

ENV PORT=8000

ENTRYPOINT [ "/opt/app/docker/docker-entrypoint.sh" ]
CMD [ "server" ]