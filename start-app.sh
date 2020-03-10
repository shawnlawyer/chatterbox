#!/bin/bash

screen -dmS CHAT bash -c 'python3 flask-chat.py'
screen -dmS ADMIN bash -c 'python3 flask-admin.py'
