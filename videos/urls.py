from django.conf.urls.defaults import *
from jinjasupport import jenv

urlpatterns = patterns('',
    (r'^/?$', 'videos.views.index'),
    (r'^/upload/?$', 'videos.views.upload_videos'),
)