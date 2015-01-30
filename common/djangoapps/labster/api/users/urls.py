from django.conf.urls import patterns, url

from labster.api.users.views import UserCreate, UserView


urlpatterns = patterns('',  # nopep8
    url('^$', UserCreate.as_view(), name='users'),
    url('^(?P<user_id>\d+)/$', UserView.as_view(), name='users'),
)
