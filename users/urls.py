from django.conf.urls.defaults import *

urlpatterns = patterns('',
  url(r'^/register/$', 'users.views.register', name="signup_url"),
)

# @TODO REPLACE THIS WITH BETTER LOGOUT VIEW
urlpatterns += patterns('django.contrib.auth',
    url(r'^/login/$','views.login', {'template_name': 'admin/login.html'}, name="signin_url"),
    url(r'^/logout/$','views.logout', name="signout_url"),
)
