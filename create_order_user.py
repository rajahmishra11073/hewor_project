import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hewor_project.settings')
django.setup()

from django.contrib.auth.models import User

username = "Hewor.order"
password = "Hewor.order@a2025M"
email = "order_admin@hewor.in"

try:
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(username=username, password=password, email=email)
        print(f"User {username} created successfully.")
    else:
        print(f"User {username} already exists.")
except Exception as e:
    print(f"Error creating user: {e}")
