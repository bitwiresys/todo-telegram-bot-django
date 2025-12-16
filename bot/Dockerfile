FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY backend /app/backend
COPY bot /app/bot

RUN pip install --no-cache-dir .

RUN addgroup --system app && adduser --system --ingroup app app \
  && chown -R app:app /app

USER app

CMD ["python", "-m", "bot.main"]
