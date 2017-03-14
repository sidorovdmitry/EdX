"""
This file contains celery tasks for labster_course_license app.
"""
from django.utils.translation import ugettext as _
from lms import CELERY_APP
from celery.utils.log import get_task_logger
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from xmodule.modulestore.django import modulestore
from labster_course_license.models import LicensedCoursewareItems, CourseLicense
from labster_course_license.utils import SimulationValidationError, get_course_blocks_info


log = get_task_logger(__name__)


@CELERY_APP.task
def update_course_access(course_id):
    """
    Updates master course access structure.

    Args:
        course_id(str): A string representation of course identifier
        available_simulations(list): list of licensed simulations for course

    Returns:
        None

    """
    try:
        course_key = CourseKey.from_string(course_id)
        update_course_access_structure(course_key)
    except InvalidKeyError as ex:
        log.error("Course %s error: %s", course_id, ex)
    except SimulationValidationError as err:
        log.error(
            _((
                'Please verify LTI URLs are correct for the following simulations:\n\n {}'
            ).format(
                '\n\n'.join(
                    'Simulation name is "{}"\nSimulation id is "{}"\nError message: {}'.format(
                        sim_name, sim_id, err_msg
                    ) for sim_name, sim_id, err_msg in err.message
                )
            ))
        )


def update_course_access_structure(course_key):
    """
    Fetch course licensed simulations structure info and save it for override provider.
    """
    store = modulestore()
    with store.bulk_operations(course_key):
        lti_blocks = store.get_items(course_key, qualifiers={'category': 'lti'})
        # Filter a list of lti blocks to get only blocks with simulations.
        simulations = (block for block in lti_blocks if '/simulation/' in block.launch_url)
        course_license = CourseLicense.get_license(course_key)
        licensed_simulations = course_license.simulations
        course_info = get_course_blocks_info(simulations, licensed_simulations)
        # store licensed blocks info
        for block, block_simulations in course_info.items():
            lci, created = LicensedCoursewareItems.objects.get_or_create(block=block.location)
            lci.simulations = block_simulations
            lci.save()
