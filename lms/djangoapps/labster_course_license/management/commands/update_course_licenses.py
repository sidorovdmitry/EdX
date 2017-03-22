"""
A command to update an access course structure.

When we apply license, Labster API is requested for list of simulations in it.
To exclude manual apply of all licenses we need this command.

Also sends `course_published` signal in the end for each master course
to trigger an update of course blocks simulations.
"""
import logging
from django.core.management.base import NoArgsCommand
from lms.djangoapps.ccx.models import CustomCourseForEdX
from xmodule.modulestore.django import SignalHandler

from labster_course_license.models import CourseLicense
from labster_course_license.views import LabsterApiError, get_licensed_simulations
from labster_course_license.utils import get_consumer_keys


class Command(NoArgsCommand):
    """
    The actual update_course_licenses command to update simulations.
    """

    help = "Update course licenses' simulations."

    def handle_noargs(self, **options):
        # We don't want to see logs about requests to Labster API
        logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.ERROR)

        cnt = 0
        courses = set()
        for course_license in CourseLicense.objects.all():
            ccx_id = course_license.course_id.ccx
            ccx = CustomCourseForEdX.objects.get(pk=ccx_id)
            consumer_keys, __ = get_consumer_keys(ccx)
            try:
                licensed_simulations_ids = get_licensed_simulations(consumer_keys)
            except LabsterApiError as ex:
                print("Failed to update `%s` license simulations: %s" % (course_license.license_code, ex))
                continue
            print("`%s` license simulations: %s" % (course_license.license_code, licensed_simulations_ids))
            course_license.simulations = list(licensed_simulations_ids)
            course_license.save()
            cnt += 1
            courses.add(ccx.course.id)
        print("Updated %d licenses" % cnt)

        for course_key in courses:
            SignalHandler.course_published.send(sender='management_task', course_key=course_key)
