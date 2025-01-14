FROM python:3.12.8-slim

ENV PYTHONUNBBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN useradd -m -r appuser \
    && chown -R appuser /app

COPY --chown=appuser:appuser . /app/

USER appuser

EXPOSE 8000

CMD ["chmode", "+x", "run.sh"]