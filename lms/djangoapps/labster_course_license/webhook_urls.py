"""
URL for the Labster Course License webhook endpoint.
"""
from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from labster_course_license.views import LicensedSimulationsUpdateView


urlpatterns = patterns('',
    url(
        r'^update/?$',
        csrf_exempt(LicensedSimulationsUpdateView.as_view()), name='labster_license_update'
    ),
)