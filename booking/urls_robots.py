from django.urls import path
from django.http import HttpResponse


def robots_txt(request):
	content = """
User-agent: *
Disallow: /admin/
Allow: /

Sitemap: /sitemap.xml
""".strip()
	return HttpResponse(content, content_type="text/plain")

urlpatterns = [
	path('', robots_txt, name='robots_txt'),
]

