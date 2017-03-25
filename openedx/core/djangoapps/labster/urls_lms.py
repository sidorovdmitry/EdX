"""
Labster API URI specification.

Patterns here should simply point to version-specific patterns.
"""
from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(
        r'^course/enroll/?$', 'openedx.core.djangoapps.labster.course.views.ccx_invite',
        name='ccx_invite'
    )
)
