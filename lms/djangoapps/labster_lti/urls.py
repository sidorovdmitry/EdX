from django.conf.urls import patterns, url


urlpatterns = patterns('labster_lti.views',  # nopep8
    url('^(?P<lab_slug>.+)/(?P<provider>.+)/iframe/$', 'iframe', name='labster_lti_iframe'),
    url('^(?P<lab_slug>.+)/lab/$', 'lab', name='labster_lti_lab'),
    url('^(?P<lab_slug>.+)/lab/Settings.xml$', 'settings_xml', name='labster_lti_lab_settings'),
    url('^(?P<lab_slug>.+)/lab/Server.xml$', 'server_xml', name='labster_lti_lab_server'),
    url('^(?P<lab_slug>.+)/lab/Platform.xml$', 'platform_xml', name='labster_lti_lab_platform'),
)
