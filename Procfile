web: python manage.py migrate && gunicorn hewor_project.wsgi --bind 0.0.0.0:$PORT --timeout 120 --access-logfile - --error-logfile - --log-level debug
