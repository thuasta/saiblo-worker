FROM busybox:1.37

WORKDIR /app

COPY entrypoint.sh .

# Sleep for 10 seconds to simulate a long running process.
RUN sleep 10

ENTRYPOINT ["sh", "entrypoint.sh"]
