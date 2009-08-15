from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^/?$', 'videos.views.index'),
    (r'^/upload/?$', 'videos.views.upload_videos'),
    (r'^/simple_upload/?$', 'videos.views.simple_upload_videos'),
)