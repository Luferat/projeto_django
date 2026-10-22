from django.conf import settings

def global_context(request):
    return {
        'site_name': settings.SITENAME,
    }