from django.conf import settings
from django.conf.urls import patterns, include, url


urlpatterns = patterns('labster',  # nopep8
    url('^api/', include('labster.api_urls', namespace='labster-api')),
    url('^internal/', include('labster_backoffice.urls')),

    url('^login-by-token/', 'users.views.login_by_token', name='labster_login_token'),
    url('^activate/(?P<activation_key>\w+)/$', 'users.views.activate_user_email', name='labster_activate'),

    url('^enroll-student-voucher/', 'lms.views.enroll_student_voucher', name='labster_enroll_student_voucher'),
    url('^enroll-student-course/', 'lms.views.enroll_student_course', name='labster_enroll_student_course'),

    url('^contact-form/$', 'landing.views.contact_form', name='labster_contact_form'),
    url('^fetch-career-data/$', 'landing.views.fetch_career_data', name='labster_fetch_career_data'),

    url('^lab/{}/(?P<pk>\d+)/result/$'.format(settings.COURSE_ID_PATTERN),
        'lms.views.lab_result', name='labster_lab_result'),
    url('^lab/{}/(?P<pk>\d+)/adaptive-test-result/$'.format(settings.COURSE_ID_PATTERN),
        'lms.views.adaptive_test_result', name='labster_adaptive_test_result'),

    url('^demo-lab/$', 'lms.views.demo_lab', name='labster_demo_lab'),
)
