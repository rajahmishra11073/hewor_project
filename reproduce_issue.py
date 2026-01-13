
import os
import django
from django.db import IntegrityError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hewor_project.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import Profile

def run_test():
    print("Testing Profile Creation without Phone Number...")
    
    # Clean up previous test users
    User.objects.filter(username__startswith='test_google_').delete()
    
    try:
        # User 1
        u1 = User.objects.create_user(username='test_google_1', email='t1@example.com')
        p1 = Profile.objects.create(user=u1, phone_number=None) 
        print("User 1 Profile Created with None phone.")
        
        # User 2
        u2 = User.objects.create_user(username='test_google_2', email='t2@example.com')
        p2 = Profile.objects.create(user=u2, phone_number=None) # Should SUCCEED now
        print("User 2 Profile Created with None phone.")
        
    except IntegrityError as e:
        print(f"FAILED: IntegrityError still occurred: {e}")
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
    finally:
        # Cleanup
        User.objects.filter(username__startswith='test_google_').delete()

if __name__ == "__main__":
    run_test()
