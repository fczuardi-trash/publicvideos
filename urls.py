from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import login, logout

admin.autodiscover()

urlpatterns = patterns('',
  (r'^admin/(.*)', admin.site.root),
  (r'^users/login/$', login, {'template_name':'users/login.html'}),
  (r'^users/logout/$', logout),
  # (r'^users', include('users.urls')),
  (r'^clips', include('videos.urls')),
  (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
