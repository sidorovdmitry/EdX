"""
A command to update an access course structure.

When we apply license, Labster API is requested for list of simulations in it.
To exclude manual apply of all licenses we need this command.

Also sends `course_published` signal in the end for each master course
to trigger an update of course blocks simulations.
"""
import json
from django.core.management.base import BaseCommand, CommandError
from opaque_keys import InvalidKeyError
from lms.djangoapps.ccx.models import CustomCourseForEdX

from labster_course_license.models import CourseLicense
from labster_course_license.tasks import update_course_access_structure


class Command(BaseCommand):
    """
    This command updates CourseLicense simulations and builds initial course access structure.
    """

    help = "Update course licenses' simulations and courses blocks structure."
    args = '<import path>'

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Please provide correct path to import data.')

        try:
            with open(args[0], 'r') as json_dump:
                data = json.load(json_dump)
        except IOError:
            raise CommandError("Cannot open file `{}`".format(args[0]))

        cnt = 0
        courses = set()

        for course_license in CourseLicense.objects.all():
            licensed_simulations_ids = data.get(course_license.license_code)
            if licensed_simulations_ids and course_license.simulations != licensed_simulations_ids:
                print("Updating `%s` license simulations: %s" % (course_license.license_code, licensed_simulations_ids))
                course_license.simulations = licensed_simulations_ids
                course_license.save()
                cnt += 1

            # add course id for future update
            try:
                ccx_id = course_license.course_id.ccx
                ccx = CustomCourseForEdX.objects.get(pk=ccx_id)
                courses.add(ccx.course.id)
            except CustomCourseForEdX.DoesNotExist:
                pass

        print("Updated %d licenses" % cnt)

        for course_key in courses:
            try:
                update_course_access_structure(course_key)
                print("Course %s blocks structure was updated successfully." % str(course_key))
            except InvalidKeyError as ex:
                print("Course %s structure update error: %s", str(course_key), ex)
