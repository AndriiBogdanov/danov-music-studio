"""
URL configuration for danovmusic_studio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from booking.sitemaps import I18nStaticViewSitemap
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/en/', permanent=False)),
    path('i18n/', include('django.conf.urls.i18n')),
    path('robots.txt', include('booking.urls_robots')),
]

urlpatterns += i18n_patterns(
    path(f'{settings.ADMIN_URL}', admin.site.urls),
    path('', include('booking.urls')),
)

# Sitemap
sitemaps = {
    'static': I18nStaticViewSitemap,
}
urlpatterns += [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap')
]

# Serve static files in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) if hasattr(settings, 'MEDIA_URL') else []

# Custom error handlers
handler400 = 'booking.views.error_400'
handler403 = 'booking.views.error_403'
handler404 = 'booking.views.error_404'
handler500 = 'booking.views.error_500'
