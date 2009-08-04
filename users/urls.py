from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^/register?/$', 'users.views.register'),
)