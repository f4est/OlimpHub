# Procfile
web: gunicorn olimphub_project.wsgi:application --bind 0.0.0.0:$PORT --log-file -
release: python manage.py migrate --noinput
