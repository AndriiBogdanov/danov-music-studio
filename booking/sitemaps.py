from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
	changefreq = 'weekly'
	priority = 0.8

i18n_locales = ['en', 'ru', 'uk', 'de']

class I18nStaticViewSitemap(Sitemap):
	changefreq = 'weekly'
	priority = 0.8

	def items(self):
		return [
			('booking:home', {}),
			('booking:about', {}),
			('booking:services', {}),
			('booking:equipment', {}),
			('booking:portfolio', {}),
			('booking:artists', {}),
			('booking:contact', {}),
			('booking:booking', {}),
		]

	def location(self, item):
		# By default reverse will respect current language; we enumerate with hreflang separately
		return reverse(item[0], kwargs=item[1])

	def alternates(self, item, request, obj):
		# Django 5.2 sitemaps supports xhtml:link alternates via get_urls; we emulate manually
		return []

