FROM python:3.11.2-slim AS build-env

WORKDIR /app

COPY requirements.txt .

RUN pip install --disable-pip-version-check --no-cache-dir -r requirements.txt

FROM gcr.io/distroless/python3@sha256:d9fd857eb4a7639c5de33a65582aebe0339bd4e15e2551de27a1d95f73aa0a82

WORKDIR /app

COPY --from=build-env /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages

COPY . .

ENTRYPOINT ["python", "main.py"]
