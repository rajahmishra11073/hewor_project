import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hewor_project.settings')
django.setup()

from core.models import SiteSetting

def init_settings():
    setting, created = SiteSetting.objects.get_or_create(id=1)
    
    # Ensure defaults are set if they are empty
    changes = False
    if not setting.case_studies_title:
        setting.case_studies_title = "Client Success Stories"
        changes = True
    if not setting.case_studies_subtitle:
        setting.case_studies_subtitle = "Real results for real clients."
        changes = True
    if not setting.case_studies_description:
        setting.case_studies_description = "Discover how we help academicians and professionals stand out."
        changes = True
        
    if changes or created:
        setting.save()
        print("Site Settings Initialized/Updated.")
    else:
        print("Site Settings already present.")

if __name__ == "__main__":
    init_settings()
