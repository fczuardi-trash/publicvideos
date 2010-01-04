from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^$', 'videos.views.index'),
  (r'^clip', include('videos.urls_production')),
  (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
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