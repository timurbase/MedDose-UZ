web: python manage.py migrate && python manage.py collectstatic --no-input && gunicorn meddose.wsgi:application --bind 0.0.0.0:$PORT
