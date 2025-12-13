# Benchmark Test Runner
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /usr/src/app

RUN pip --disable-pip-version-check install --no-cache-dir --no-compile marshmallow_dataclass colorlog pyYAML confluent_kafka numpy polars scikit-learn torch progressbar2

COPY src/test_runner ./src/test_runner
COPY src/sql/entering_processed/activity_last_three_minutes.sql src/sql/entering_processed/activity_last_three_minutes.sql
COPY src/benchmark_config.yaml ./src/benchmark_config.yaml
COPY data ./data

RUN rm -rf /root/.cache

CMD ["tail", "-f", "/dev/null"]
