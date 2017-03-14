"""
Models for the Labster License.
"""
import logging
from django.db import models
from django_extensions.db.fields.json import JSONField
from xmodule_django.models import CourseKeyField, OpaqueKeyField, UsageKeyField  # pylint: disable=import-error


log = logging.getLogger(__name__)


class CourseLicense(models.Model):
    """
    A Labster License with related simulations for course.
    """
    course_id = CourseKeyField(max_length=255, db_index=True)
    license_code = models.CharField(max_length=255, db_index=True)
    simulations = JSONField()

    @classmethod
    def get_license(cls, course_id):
        ret = None
        try:
            ret = cls.objects.get(course_id=course_id)
        except cls.DoesNotExist:
            pass
        return ret

    @classmethod
    def set_license(cls, course_id, license_code):
        course_license, __ = cls.objects.get_or_create(course_id=course_id, license_code=license_code)
        return course_license

    def __unicode__(self):
        return unicode("%s, %s" % (self.ccx_id, self.license_code))


class LicensedCoursewareItems(models.Model):
    """
    Stores all licensed simulations within block including ones from child blocks.
    """
    block = UsageKeyField(max_length=255, db_index=True)
    simulations = JSONField()

    def __unicode__(self):
        return unicode("%s, %s" % (self.block, self.simulations))
