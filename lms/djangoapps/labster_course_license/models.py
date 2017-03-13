"""
Models for the Labster License.
"""
import logging
import json
from django.db import models

from ccx_keys.locator import CCXLocator
from xmodule_django.models import CourseKeyField, OpaqueKeyField, UsageKeyField  # pylint: disable=import-error


log = logging.getLogger(__name__)


def add_simulations(inst, sim_list):
    """
    Associate licensed simulations to instance.
    """
    print('______   adding simulations to %s' % inst.__class__.__name__)
    print(sim_list)
    if not isinstance(sim_list, set):
        return

    simulations = set(inst.simulations.all().values_list('code', flat=True))

    print('current list', simulations)
    if simulations != set(sim_list):
        print('updating')
        inst.simulations.clear()
        related_sims = [Simulation.objects.get_or_create(code=simulation)[0] for simulation in sim_list]
        if related_sims:
            inst.simulations.add(*related_sims)
    else:
        log.debug('No changes in %s', inst.license_code)


class CourseLicense(models.Model):
    """
    A Labster License with related simulations for course.
    """
    course_id = CourseKeyField(max_length=255, db_index=True)
    license_code = models.CharField(max_length=255, db_index=True)
    simulations = models.ManyToManyField(Simulation, related_name='courselicenses')

    def add_simulations(self, sim_list):
        """
        Associate licensed simulations to course license.
        """
        add_simulations(self, sim_list)

    def get_simulations_set(self):
        return set(self.simulations.all().values_list('code', flat=True))

    @classmethod
    def get_license(cls, course_id):
        try:
            return cls.objects.get(course_id=course_id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def set_license(cls, course_id, license_code):
        course_license, __ = cls.objects.get_or_create(course_id=course_id, license_code=license_code)
        return course_license

    def __unicode__(self):
        return unicode("%s, %s" % (self.course_id, self.license_code))





class LicensedCoursewareItems(models.Model):
    """
    Stores all licensed simulations within block including ones from child blocks.
    """
    block = UsageKeyField(max_length=255, db_index=True)
    simulations = models.ManyToManyField(Simulation, related_name='licenseditems')

    def add_simulations(self, sim_list):
        """
        Associate licensed simulations to course license.
        """
        add_simulations(self, sim_list)
