from django.conf.urls import patterns, url


urlpatterns = patterns('labster_lti.views',  # nopep8
    url('^(?P<lab_slug>.+)/(?P<provider>.+)/iframe/$', 'iframe', name='labster_lti_iframe'),
    url('^(?P<lab_slug>.+)/lab/$', 'lab', name='labster_lti_lab'),
)
