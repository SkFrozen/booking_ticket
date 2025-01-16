FROM python:3.12.8-alpine

ENV PYTHONUNBBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN addgroup -g 10001 user_app_group \
    && adduser -D -h /app -u 10002 user_app user_app_group \
    && chown -R user_app:user_app_group /app

RUN mkdir -p /app/media

COPY . /app/

RUN chown -R user_app:user_app_group /app

USER user_app

EXPOSE 8000

RUN chmod +x run.sh