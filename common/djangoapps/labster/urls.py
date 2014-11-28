from django.conf import settings
from django.conf.urls import patterns, include, url


urlpatterns = patterns('labster',  # nopep8
    url('^api/', include('labster.api_urls', namespace='labster-api')),
    url('^lab/dummy-post/$', 'lms.views.dummy_post', name='labster_dummy_post'),
    url('^lab/{}/(?P<pk>\d+)/result/$'.format(settings.COURSE_ID_PATTERN),
        'lms.views.lab_result', name='labster_lab_result'),
    url('^demo-lab/$', 'lms.views.demo_lab', name='labster_demo_lab'),
)
