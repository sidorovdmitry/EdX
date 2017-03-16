"""
Course License test factories.
"""
import factory
from factory.django import DjangoModelFactory
from ccx_keys.locator import CourseLocator

from labster_course_license.models import CourseLicense


class CourseLicenseFactory(DjangoModelFactory):
    class Meta(object):
        model = CourseLicense

    course_id = CourseLocator(org='edX', course='toy', run='2012_Fall')
    license_code = factory.Sequence(u'license{0}'.format)
