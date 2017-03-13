"""
This file contains signals for labster_course_license app.
"""
import logging
from django.dispatch.dispatcher import receiver
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import SignalHandler
from labster_course_license.models import CourseLicense


log = logging.getLogger(__name__)


@receiver(SignalHandler.course_published)
def on_course_publish(sender, course_key, **kwargs):  # pylint: disable=unused-argument
    """
    Will receive a delegated 'course_published' signal
    and kick off a celery task to update the course access structure.
    """
    # prevent from circular import
    from .tasks import update_course_access
    import traceback

    print("         got course update signal, starting celery task...")
    try:
        course_license = CourseLicense.get_license(CourseKey.from_string(course_key))
        licensed_simulations = course_license.get_simulations_set()
    except:
        traceback.print_exc()
    update_course_access.delay(unicode(course_key), licensed_simulations)
    log.info(u'Added task to update access course structure for course "%s" to the task queue', course_key)
