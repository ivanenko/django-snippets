from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.apps import apps
from django.views.generic import TemplateView
import os

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

def get_urls():
    urls = []
    for appConfig in apps.get_app_configs():
        if appConfig.name.startswith('django.'):
            continue

        if os.path.isfile(os.path.join(appConfig.path, "urls.py")):
            urls.append(url(r'^%s/' % appConfig.label, include('%s.urls' % appConfig.name, namespace=appConfig.label, app_name=appConfig.label)))

        if os.path.isfile(os.path.join(appConfig.path, "absolute_urls.py")):
            urls.append(url('', include('%s.absolute_urls' % appConfig.name)))

    return urls


urlpatterns = patterns('',
    #url('^', include('django.contrib.auth.urls')),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name="home"),

    # Examples:
    # url(r'^$', '{{ project_name }}.views.home', name='home'),
    # url(r'^{{ project_name }}/', include('{{ project_name }}.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    *get_urls()
)

# Uncomment the next line to serve media files in dev.
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns += patterns('',
#                             url(r'^__debug__/', include(debug_toolbar.urls)),
#                             )