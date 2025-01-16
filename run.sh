if [ "$DATABASE_ENGINE" = "postgresql" ]
then
    echo "Waiting for postgres..."
    
    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
        sleep 1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate --no-input

export DJANGO_COLLECT_STATIC=1
python manage.py collectstatic --no-input

if [ -f /shared/stripe_endpoint_secret.txt ]
then
    echo "The file with key was found"
    STRIPE_ENDPOINT_SECRET=$(cat /shared/stripe_endpoint_secret.txt)
    export STRIPE_ENDPOINT_SECRET
    echo "The value of STRIPE_ENDPOINT_SECRET in run.sh accepted"
else
    echo "STRIPE_ENDPOINT_SECRET is null"
fi

python manage.py createsuperuser --no-input
gunicorn -b 0.0.0.0:8000 booking_ticket.wsgi:application

