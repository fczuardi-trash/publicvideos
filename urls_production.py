from django.conf import settings
from django.conf.urls.defaults import *
from lib.jinjasupport import jenv

urlpatterns = patterns('',
  (r'^$', 'videos.views.index'),
  (r'^sitemap.xml$', 'videos.views.sitemap_index'),
  (r'^sets\/?$', 'videos.views.list_sets'),
  (r'^set/(?P<set_slug>[^\/]*)\/?$', 'videos.views.index'),
  (r'^about/?$', 'django.views.generic.simple.direct_to_template', {'template': 'website/about.html','template_loader':jenv}),
  (r'^robots.txt?$', 'django.views.generic.simple.direct_to_template', {'template': 'website/robots.txt','template_loader':jenv}),
  (r'^clip', include('videos.urls_production')),
  (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

# external links that appears on the beta-coming soon page
urlpatterns += patterns('django.views.generic.simple',
  url(r'^blog/?$', 'redirect_to', 
    {'url': 'http://publicvideos.posterous.com/'}, 
    name="blog_url"),
  url(r'^development/?$', 'redirect_to', 
    {'url': 'https://launchpad.net/publicvideos'}, 
    name="development_url"),
  url(r'^launch_notification/?$', 'redirect_to', 
    {'url': 'http://spreadsheets.google.com/viewform?formkey=dEFNRU96SXBkWFdjc2pWeXBZNE5KRHc6MA..'}, 
    name="launch_notification_form_url"),
  url(r'^join_beta/?$', 'redirect_to', 
    {'url': 'http://spreadsheets.google.com/viewform?formkey=dHJPZzczbVhuR0tnX0doaFRJVE5IX1E6MA..'}, 
    name="join_beta_form"),
  url(r'^faq/?$', 'redirect_to', 
    {'url': 'http://www.formspring.me/publicvideos'}, 
    name="faq_url"),
)

urlpatterns += patterns('',
  (r'^(.[a-z0-9]+)(.*)', 'videos.views.show')
)