FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml
COPY backend /app/backend
COPY bot /app/bot
COPY pytest.ini /app/pytest.ini

RUN pip install --no-cache-dir .

COPY backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN addgroup --system app && adduser --system --ingroup app app \
  && chown -R app:app /app \
  && chown app:app /entrypoint.sh

USER app

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "backend.config.wsgi:application", "-b", "0.0.0.0:8000", "-w", "2"]
