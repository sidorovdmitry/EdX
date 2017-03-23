"""
Models for the Labster License.
"""
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django_extensions.db.fields.json import JSONField
from ccx_keys.locator import CCXLocator
from xmodule_django.models import OpaqueKeyField, UsageKeyField  # pylint: disable=import-error


log = logging.getLogger(__name__)


class CCXLocatorField(OpaqueKeyField):
    """
    A django Field that stores a CCXLocator object as a string.
    """
    description = "A CCXLocator object, saved to the DB in the form of a string"
    KEY_CLASS = CCXLocator


class CourseLicense(models.Model):
    """
    A Labster License with related simulations for course.
    """
    course_id = CCXLocatorField(max_length=255, db_index=True, unique=True, help_text="CCXCourse locators only")
    license_code = models.CharField(max_length=255, db_index=True)
    simulations = JSONField(help_text="List of course licensed simulations, stored as json string value")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)

    @classmethod
    def get_license(cls, course_id):
        """
        Return license by course key.
        """
        try:
            return cls.objects.get(course_id=course_id)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def set_license(cls, course_id, license_code):
        """
        Save course license.
        """
        course_license, created = cls.objects.get_or_create(
            course_id=course_id, defaults={'license_code': license_code.strip()}
        )
        if not created:
            course_license.license_code = license_code
            course_license.save()
        return course_license

    def __unicode__(self):
        return unicode("%s, license='%s', simulations=%s" % (self.course_id, self.license_code, self.simulations))


class LicensedCoursewareItems(models.Model):
    """
    Stores all licensed simulations within block including ones from child blocks.
    """
    block = UsageKeyField(max_length=255, db_index=True)
    simulations = JSONField(help_text="List of block licensed simulations, stored as json string value")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)

    def __unicode__(self):
        return unicode("%s, simulations=%s" % (self.block, self.simulations))
