"""
This file contains celery tasks for labster_course_license app.
"""
from lms import CELERY_APP
from celery.utils.log import get_task_logger
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from xmodule.modulestore.django import modulestore
from labster_course_license.models import LicensedCoursewareItems
from labster_course_license.utils import get_course_blocks_info, validate_simulations_ids


log = get_task_logger(__name__)


@CELERY_APP.task
def update_course_access(course_id):
    """
    Updates master course access structure.

    Args:
        course_id(str): A string representation of course identifier

    Returns:
        None

    """
    try:
        course_key = CourseKey.from_string(course_id)
        update_course_access_structure(course_key)
        log.info("Course %s blocks structure was updated successfully.", course_id)
    except InvalidKeyError as ex:
        log.error("Course %s error: %s", course_id, ex)


def update_course_access_structure(course_key):
    """
    Fetch course licensed simulations structure info and save it for override provider.
    """
    if not isinstance(course_key, CourseKey):
        log.error("%s is not CourseKey instance. Canceled update.", course_key)
        return
    store = modulestore()
    with store.bulk_operations(course_key):
        valid_simulations, errors = validate_simulations_ids(course_key)
        if errors:
            log.error(
                "Invalid LTI URLs in the following simulations: %s",
                ' '.join('{}:{}:{}'.format(sim_name, sim_id, err_msg) for sim_name, sim_id, err_msg in errors)
            )
        course_info = get_course_blocks_info(valid_simulations)
        # store licensed blocks info
        course_blocks = []
        for block, block_simulations in course_info.items():
            simulations = list(block_simulations)
            log.info("Updating block %s structure with simulations %s", block.display_name, simulations)
            lci, __ = LicensedCoursewareItems.objects.get_or_create(block=block.location, course_id=course_key)
            if lci.simulations != simulations:
                lci.simulations = simulations
                lci.save()
            course_blocks.append(block.location)

        # remove unused blocks for course
        LicensedCoursewareItems.objects.filter(course_id=course_key).exclude(block__in=course_blocks).delete()
