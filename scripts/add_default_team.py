import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hewor_project.settings')
django.setup()

from core.models import TeamMember

def create_founder():
    if not TeamMember.objects.filter(name="Rajesh Kumar Mishra").exists():
        TeamMember.objects.create(
            name="Rajesh Kumar Mishra",
            role="FOUNDER & CEO",
            quote="I started Hewor with a simple mission: To let students study while we handle the grunt work. We are the future of academic assistance.",
            linkedin_url="https://linkedin.com/in/rajeshkumarmishra",
            twitter_url="https://twitter.com/rajeshkumarmishra",
            order=1
        )
        print("Created default Team Member: Rajesh Kumar Mishra")
    else:
        print("Team Member already exists.")

if __name__ == "__main__":
    create_founder()
