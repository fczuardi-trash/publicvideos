from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^\/?$', 'videos.views.show'),
    (r'^/(?P<id>[^\/]+)\/?$', 'videos.views.show'),
    url(r'^s/?$', 'videos.views.index', name="clips_index_url"),
    (r'^s/upload/?$', 'videos.views.upload_videos'),
    (r'^s/simple_upload/?$', 'videos.views.simple_upload_videos'),
)