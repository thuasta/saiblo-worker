#!/bin/sh

# Check if running in --privileged mode
if ! (mkdir -p /tmp/rootless_test && mount -t tmpfs tmpfs /tmp/rootless_test > /dev/null 2>&1); then
    echo "Not running in --privileged mode"
    exit 1
fi
umount /tmp/rootless_test
rmdir /tmp/rootless_test

dockerd-entrypoint.sh > /dev/null 2>&1 &

# Wait for the Docker daemon to start up
echo "Waiting for the Docker daemon to start up..."
while ! docker info > /dev/null 2>&1; do
    sleep 0
done

python main.py $@
