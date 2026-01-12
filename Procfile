web: python manage.py collectstatic --noinput && python manage.py migrate && gunicorn hewor_project.wsgi --bind 0.0.0.0:$PORT
