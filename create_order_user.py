import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hewor_project.settings')
django.setup()

from django.contrib.auth.models import User

username = "Hewor.order"
password = "Hewor.order@a2025M"
email = "order_admin@hewor.in"

try:
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.email = email
        print(f"User {username} created successfully.")
    else:
        print(f"User {username} already exists. Updating password...")
    
    user.set_password(password)
    user.save()
    print(f"Password for {username} set to: {password}")
except Exception as e:
    print(f"Error creating user: {e}")
