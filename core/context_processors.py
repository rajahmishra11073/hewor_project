import os

def google_analytics(request):
    """Add Google Analytics ID to all templates"""
    return {
        'google_analytics_id': os.environ.get('GOOGLE_ANALYTICS_ID', '')
    }
