from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from lib.jinjasupport import jenv
#from videos.models import Video

admin.autodiscover()

urlpatterns = patterns('',
  url(r'^$', 'videos.views.index', name="site_index_url"),
  (r'^account/', include('django_authopenid.urls')),
  (r'^clip', include('videos.urls')),
  (r'^users', include('users.urls')),
  (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
  (r'^admin/(.*)', admin.site.root),
#  (r'^jinja2-generic-views-test$', 'django.views.generic.create_update.create_object', {'model': Video,'template_loader':jenv}),
)

# external links that appears on the beta-coming soon page
urlpatterns += patterns('django.views.generic.simple',
  url(r'^development/$', 'redirect_to', 
    {'url': 'https://launchpad.net/publicvideos'}, 
    name="development_url"),
  url(r'^launch_notification/$', 'redirect_to', 
    {'url': 'http://spreadsheets.google.com/viewform?formkey=dEFNRU96SXBkWFdjc2pWeXBZNE5KRHc6MA..'}, 
    name="launch_notification_form_url"),
  url(r'^join_beta/$', 'redirect_to', 
    {'url': 'http://spreadsheets.google.com/viewform?formkey=dHJPZzczbVhuR0tnX0doaFRJVE5IX1E6MA..'}, 
    name="join_beta_form"),
)

urlpatterns += patterns('',
  (r'^(.[a-z0-9]+)(.*)', 'videos.views.show')
)