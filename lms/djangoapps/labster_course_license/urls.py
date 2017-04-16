"""
URLs for the Labster Course License Feature.
"""
from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt
from labster_course_license.views import LicensedSimulationsUpdateView


urlpatterns = patterns('',
    url(
        r'^labster_license/?$',
        'labster_course_license.views.license_handler', name='labster_license_handler'
    ),
)
