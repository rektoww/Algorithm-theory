FROM python:3.13-slim

# Немедленный вывод логов и кодировка UTF-8.
ENV PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1
WORKDIR /app

COPY requirements-core.txt .
RUN pip install --no-cache-dir -r requirements-core.txt
COPY lab04 ./lab04
COPY tests ./tests
COPY pyproject.toml .

ENTRYPOINT ["python", "-m", "lab04.cli"]
CMD ["--help"]
