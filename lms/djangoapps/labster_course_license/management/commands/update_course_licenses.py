"""
A command to update an access course structure.

When we apply license, Labster API is requested for list of simulations in it.
To exclude manual apply of all licenses we need this command.

Also sends `course_published` signal in the end for each master course
to trigger an update of course blocks simulations.
"""
import logging
from django.core.management.base import NoArgsCommand
from django.conf import settings
from lms.djangoapps.ccx.models import CustomCourseForEdX
from xmodule.modulestore.django import SignalHandler

from labster_course_license.models import CourseLicense
from labster_course_license.views import LabsterApiError, get_licensed_simulations, _send_request
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
        licenses_keys = []
        print("Processing...")
        for course_license in CourseLicense.objects.all():
            ccx_id = course_license.course_id.ccx
            ccx = CustomCourseForEdX.objects.get(pk=ccx_id)
            try:
                courses.add(ccx.course.id)
                consumer_keys, __ = get_consumer_keys(ccx)
                licenses_keys.append([course_license.license_code, consumer_keys])
            except OSError as ex:
                print("Failed to get consumer keys for %s course: %s" % (ccx, ex))
                continue

        print("Requesting API for simulations...")
        licensed_simulations = self.bulk_fetch_simulations(licenses_keys)

        for license_code, simulations in licensed_simulations:
            licensed_simulations_ids = list(simulations)
            course_license = CourseLicense.objects.get(license_code=license_code)
            if course_license.simulations != licensed_simulations_ids:
                print("Updating `%s` license simulations: %s" % (course_license.license_code, licensed_simulations_ids))
                course_license.simulations = licensed_simulations_ids
                course_license.save()
                cnt += 1
            else:
                print("`%s` license simulations already up to date." % course_license.license_code)
        print("Updated %d licenses" % cnt)

        for course_key in courses:
            SignalHandler.course_published.send(sender='management_task', course_key=course_key)

    @staticmethod
    def fetch_simulations_updates(consumer_keys):
        """
        Return a list of available simulation ids for each consumer_key item.
        Raises: LabsterApiError
        """
        data = {'consumer_keys': consumer_keys}
        url = settings.LABSTER_ENDPOINTS.get('available_simulations')
        response = _send_request(url, data)
        return response

    def bulk_fetch_simulations(self, licenses_keys):
        """
        Splits API requests to smaller lists to prevent 504 error.
        """
        licensed_simulations = {}
        try:
            cnt = 0
            while len(licenses_keys):
                lngth = len(licenses_keys)
                if lngth >= 10:
                    licensed_simulations.update(self.fetch_simulations_updates(licenses_keys[0:10]))
                    del licenses_keys[:10]
                    cnt += 10
                else:
                    licensed_simulations.update(self.fetch_simulations_updates(licenses_keys))
                    del licenses_keys[:lngth - 1]
                    cnt += lngth
                print("Fetched %d items, %d left" % (cnt, len(licenses_keys)))

        except LabsterApiError as ex:
            print("Failed to fetch licensed simulations from API: %s" % ex)

        return licensed_simulations
