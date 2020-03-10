#!/bin/bash

screen -S CHAT -X quit
sleep 1
screen -wipe
screen -dmS CHAT bash -c 'python3 flask-chat.py'
