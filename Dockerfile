FROM ghcr.io/futrime/docker-python:27.5-py3.13

WORKDIR /app

COPY requirements.txt .

RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /usr/local/bin/

ENTRYPOINT ["entrypoint.sh"]
