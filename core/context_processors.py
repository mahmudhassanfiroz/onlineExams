
from .models import FooterContent
from .models import SiteSettings


def footer_content(request):
    footer = FooterContent.objects.first()
    return {'footer_content': footer}


def site_settings(request):
    settings = SiteSettings.objects.first()
    return {'site_settings': settings}