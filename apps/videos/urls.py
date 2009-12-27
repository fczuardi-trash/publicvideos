from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^/?$', 'videos.views.show'),
    (r'^s/?$', 'videos.views.index'),
    (r'^s/upload/?$', 'videos.views.upload_videos'),
    (r'^s/simple_upload/?$', 'videos.views.simple_upload_videos'),
)