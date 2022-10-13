#!/usr/bin/env sh

set -e

CMD=$1

if [[ -z "$CMD" ]]; then
    echo "No command found."
    exit 1
fi

if [[ $CMD == "server" ]]; then
    if [[ -z $PORT ]]; then
        PORT="8000"
    fi
    CMD="$CMD --port $PORT"
elif [[ $CMD == "client" ]]; then
    if [[ -z $NAME ]]; then
        echo "NAME not set. It is a required environment variable."
        exit 1
    fi
    if [[ -z $PORT ]]; then
        echo "PORT not set. It is a required environment variable."
        exit 1
    fi
    if [[ -z $SERVER_IP ]]; then
        SERVER_IP="localhost"
    fi
    if [[ -z $SERVER_PORT ]]; then
        SERVER_PORT="8000"
    fi
    CMD="$CMD --name $NAME --port $PORT --server-ip $SERVER_IP --server-port $SERVER_PORT"
else
    echo "Invalid command. Command can either be `server` or `client`"
    exit 1
fi

exec $CMD
