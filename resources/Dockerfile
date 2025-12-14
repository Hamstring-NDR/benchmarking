# Benchmark Test Runner
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /usr/src/app

COPY requirements.txt ./requirements.txt

RUN pip --disable-pip-version-check install --no-cache-dir --no-compile -r requirements.txt

COPY src ./src
COPY data ./data

RUN rm -rf /root/.cache

CMD ["tail", "-f", "/dev/null"]
