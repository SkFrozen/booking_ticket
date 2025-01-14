python manage.py migrate;

export DJANGO_COLLECT_STATIC=1;
python manage.py collectstatic --noinput;

python manage.py createsuperuser --noinput;
gunicorn -b 0.0.0.0:8000 booking_ticket.wsgi:application;