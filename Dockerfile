FROM futrime/docker-python:27.4-dind-py3.11-alpine3.21
WORKDIR /app
COPY requirements.txt .
RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt
COPY . .
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]
