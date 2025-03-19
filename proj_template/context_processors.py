from django.conf import settings

def global_settings(request):
    """
    Make global settings available to all templates
    """
    return {
        'SITE_NAME': settings.SITE_NAME,
        'SITE_VERSION': settings.SITE_VERSION,
        'DEBUG': settings.DEBUG,
    }
