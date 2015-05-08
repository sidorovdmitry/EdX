from django.conf.urls import patterns, include, url  # noqa


# urlpatterns = patterns('labster_admin.views',  # nopep8
#     url('^$', 'home', name='labster_admin_home'),
#     url('^add-teacher-to-license/$', 'add_teacher_to_license', name='labster_add_teacher_to_license'),
#     url('^duplicate-multiple-courses/$', 'duplicate_multiple_courses', name='labster_duplicate_multiple_courses'),
# )

urlpatterns = patterns('labster_admin.views',  # nopep8
    url('^labs-play-data/$', 'labs_play_data', name='labster_labs_play_data'),
)

urlpatterns = patterns('labster.cms.views',  # nopep8
    url('^duplicate-lab/$', 'duplicate_lab', name='labster_duplicate_lab'),
    url('^duplicate-course/$', 'duplicate_course_view', name='labster_duplicate_course'),
    url('^manage-lab/$', 'manage_lab_view', name='labster_manage_lab'),
    url('^update-course-block/(?P<lab_id>\d+)/$', 'update_quiz_block_view', name='labster_update_quiz_block'),
)

urlpatterns += patterns('',  # nopep8
    url('^api/', include('labster.cms_api_urls', namespace='labster-cms-api')),
    url('^internal/', include('labster_backoffice.urls', namespace='labster-backoffice')),
)
