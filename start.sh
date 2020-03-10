#!/bin/bash

export TERM=xterm


if [ "$ENVIRONMENT" == "DEV" ]; then
    if [ ! -f '/usr/local/bin/ngrok' ]; then
        wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
        unzip ngrok-stable-linux-amd64.zip
        mv ngrok /usr/local/bin/ngrok
        rm ngrok-stable-linux-amd64.zip
    fi
    if [ ! -f '/root/.ngrok2/ngrok.yml' ]; then
        ngrok authtoken ${NGROK_AUTH_TOKEN}
    fi
fi

if [ ! -d 'logs' ]; then
    mkdir -p logs
fi

. start-server.sh

. start-app.sh

#. start-tunnel.sh

#if [ "$ENVIRONMENT" == "DEV" ]; then
# screen -dmS ALEXA_ENDPOINT bash -c 'while true; do ./public_url.py > logs/endpoint.log; sleep 3660; done'
    #screen -dmS ALEXA_ENDPOINT bash -c './public_url.py'
#fi
tail -f /dev/null
