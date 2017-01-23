"""
Models for the Labster License.
"""
from django.db import models

from ccx_keys.locator import CCXLocator
from xmodule_django.models import OpaqueKeyField  # pylint: disable=import-error


class CCXLocatorField(OpaqueKeyField):
    """
    A django Field that stores a CCXLocator object as a string.
    """
    description = "A CCXLocator object, saved to the DB in the form of a string"
    KEY_CLASS = CCXLocator


class CourseLicense(models.Model):
    """
    A Labster License.
    """
    course_id = CCXLocatorField(max_length=255, db_index=True, unique=True)
    license_code = models.CharField(max_length=255, db_index=True)

    @classmethod
    def get_license(cls, course_id):
        try:
            return cls.objects.get(course_id=course_id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def set_license(cls, course_id, license_code):
        try:
            course_license = cls.objects.get(course_id=course_id)
            course_license.license_code = license_code
        except cls.DoesNotExist:
            course_license = cls.objects.create(course_id=course_id, license_code=license_code)
        course_license.save()

    def __unicode__(self):
        return unicode(repr(self))


class LicensedCoursewareItems(models.Model):
    """
    Stores all licensed simulations from block including ones from child blocks.
    """
    course_license = models.ForeignKey(CourseLicense)
    block = models.CharField(max_length=64)
    licensed_simulations = models.TextField()


class LicensedSimulations(models.Model):
    """
    Keeps cached info from Labster API about licensed simulations for license.
    """
    course_license = models.ForeignKey(CourseLicense)
    licensed_simulations = models.TextField(blank=True, null=True)
