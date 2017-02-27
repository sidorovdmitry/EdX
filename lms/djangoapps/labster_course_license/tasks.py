"""
This file contains celery tasks for labster_course_license app.
"""
import json
from lms import CELERY_APP
from lms.djangoapps.ccx.models import CustomCourseForEdX
from celery.utils.log import get_task_logger
from ccx_keys.locator import CCXLocator
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from labster_course_license.views import update_course_access_structure
from labster_course_license.models import CourseLicense, LicensedSimulations


log = get_task_logger(__name__)


@CELERY_APP.task
def update_course_access(course_id):
    """
    Updates course access structure for a course.

    Args:
        course_id(str): A string representation of course identifier

    Returns:
        None

    """
    try:
        course_key = CourseKey.from_string(course_id)
        custom_courses = CustomCourseForEdX.objects.filter(course_id=course_key)
        for ccx in custom_courses:
            ccx_locator = CCXLocator.from_course_locator(ccx.course.id, ccx.id)
            course_license = CourseLicense.get_license(ccx_locator)
            if course_license:
                licensed_simulations = json.loads(
                    LicensedSimulations.objects.get(course_license=course_license).licensed_simulations
                )
                update_course_access_structure(course_key, course_license, licensed_simulations)
    except (InvalidKeyError, LicensedSimulations.DoesNotExist) as ex:
        log.error("Course %s error: %s" % (course_id, ex))
