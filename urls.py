from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import login, logout
#from lib.jinjasupport import jenv
#from videos.models import Video

admin.autodiscover()

urlpatterns = patterns('',
  (r'^$', 'website.views.index'),
  (r'^clips', include('videos.urls')),
  (r'^users/login/$', login, {'template_name':'users/login.html'}),
  (r'^users/logout/$', logout),
  (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
  (r'^admin/(.*)', admin.site.root),
#  (r'^jinja2-generic-views-test$', 'django.views.generic.create_update.create_object', {'model': Video,'template_loader':jenv}),
)
