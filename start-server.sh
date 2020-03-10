#!/bin/bash

# For Nginx
if [ ! -d 'logs' ]; then
    mkdir -p logs
fi

nginx

