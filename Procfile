web: python manage.py collectstatic --noinput && python manage.py migrate && (python manage.py createsuperuser --noinput || true) && gunicorn django_basico.wsgi --bind 0.0.0.0:$PORT --log-file -
