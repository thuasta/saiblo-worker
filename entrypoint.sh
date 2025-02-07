#!/bin/sh

dockerd-entrypoint.sh > /dev/null 2>&1 &

# Wait for the Docker daemon to start up
while ! docker info > /dev/null 2>&1; do
    echo "Waiting for the Docker daemon to start up..."
    sleep 3
done

python main.py $@
