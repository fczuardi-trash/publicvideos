from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^/?$', 'videos.views.show'),
    (r'^/(?P<id>.+)/?$', 'videos.views.show'),
    (r'^s/?$', 'videos.views.index'),
)