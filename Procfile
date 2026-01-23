web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn hewor_project.wsgi --workers 1 --threads 8 --timeout 120 --bind 0.0.0.0:$PORT
