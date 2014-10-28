from django.conf.urls import patterns, include, url  # noqa


urlpatterns = patterns('labster.cms.views',  # nopep8
    url('^duplicate-lab/$', 'duplicate_lab', name='labster_duplicate_lab'),
    url('^duplicate-course/$', 'duplicate_course_view', name='labster_duplicate_course'),
    url('^manage-lab/$', 'manage_lab_view', name='labster_manage_lab'),
)

urlpatterns += patterns('',  # nopep8
    url('^api/', include('labster.cms_api_urls', namespace='labster-cms-api')),
)
