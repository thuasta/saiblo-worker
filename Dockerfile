FROM ghcr.io/futrime/docker-python:27.5-py3.11-alpine3.21
WORKDIR /app
COPY requirements.txt .
RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt
COPY . .
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]
