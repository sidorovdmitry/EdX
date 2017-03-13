"""
This file contains celery tasks for labster_course_license app.
"""
from django.utils.translation import ugettext as _
from lms import CELERY_APP
from celery.utils.log import get_task_logger
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from xmodule.modulestore.django import modulestore
from labster_course_license.models import LicensedCoursewareItems
from labster_course_license.utils import SimulationValidationError, get_course_blocks_info


log = get_task_logger(__name__)


@CELERY_APP.task
def update_course_access(course_id, available_simulations):
    """
    Updates master course access structure.

    Args:
        course_id(str): A string representation of course identifier
        available_simulations(list): list of licensed simulations for course

    Returns:
        None

    """
    print("         celery task in progress")
    import traceback
    try:
        course_key = CourseKey.from_string(course_id)
        update_course_access_structure(course_key, available_simulations)
        print('         updated successfully')
    except InvalidKeyError as ex:
        print('         Course %s error: %s' % (course_id, ex))
        log.error("Course %s error: %s", course_id, ex)
    except SimulationValidationError as err:
        print('         Please verify LTI URLs are correct')
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
    except Exception as ex:
        print('         Something wrong: %s' % ex)
        traceback.print_exc()


def update_course_access_structure(course_key, licensed_simulations):
    """
    Fetch course licensed simulations structure info and save it for override provider.
    """
    store = modulestore()
    with store.bulk_operations(course_key):
        lti_blocks = store.get_items(course_key, qualifiers={'category': 'lti'})
        # Filter a list of lti blocks to get only blocks with simulations.
        simulations = (block for block in lti_blocks if '/simulation/' in block.launch_url)
        course_info = get_course_blocks_info(simulations, licensed_simulations)
        # store licensed blocks info
        print('****** store')
        for block, block_simulations in course_info.items():
            print(block.display_name, block.location)
            lci, created = LicensedCoursewareItems.objects.get_or_create(block=block.location)
            if created:
                print('created')
            else:
                print('updated')
            lci.add_simulations(block_simulations)
