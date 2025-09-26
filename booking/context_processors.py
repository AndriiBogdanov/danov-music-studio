from .models import SiteSEOSettings


def seo_settings(request):
	"""Inject global SEO & analytics settings into templates as site_seo_settings."""
	settings_obj = SiteSEOSettings.objects.first()
	return {
		'site_seo_settings': settings_obj
	}



