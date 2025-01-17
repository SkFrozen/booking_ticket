# Booking flights
![Python](https://img.shields.io/badge/python-3.12-blue.svg)

<div>
  <img src="https://www.vectorlogo.zone/logos/nginx/nginx-icon.svg" alt="nginx" width="32" height="32"/>
  <img src="https://cdn.worldvectorlogo.com/logos/django.svg" alt="django" width="30" height="30"/>
  <img src="https://havola.uz/uploads/logos/90/sb4u0gqv.png" alt="celery" width="30" height="30"/>
  <img src="https://www.vectorlogo.zone/logos/redis/redis-icon.svg" alt="redis" width="30" height="30"/>
  <img src="https://www.vectorlogo.zone/logos/stripe/stripe-icon.svg" alt="stripe" width="30" height="30"/>
  <img src="https://www.vectorlogo.zone/logos/rabbitmq/rabbitmq-icon.svg" alt="rabbitmq" width="30" height="30"/>
  <img src="https://www.vectorlogo.zone/logos/postgresql/postgresql-icon.svg" alt="rabbitmq" width="30" height="30"/>
</div>

### An application for booking plane tickets
1. You can view a list of cities and destinations
2. You can view a list of planes
3. You can book flights
4. You can download your tickets

### Design

## Installation

### Docker
The most convenient and easiest way to launch a project is to use Docker Compose. 
If you don't have it yet, you can download the latest version from 
[the official website](https://github.com/docker/compose).

1. You will need to register with the [Stripe service](https://stripe.com/) and create a dashboard. Once you have created a dashboard, you can use the API secret key.

![img](img/api_keys.png)

2. Copy the contents of the `example.env` file into the `.env` file, and then complete it with your own data.
```shell
cp example.env .env
```
3. Now you can run the containers.
```shell
docker compose build
docker compose up -d
```
