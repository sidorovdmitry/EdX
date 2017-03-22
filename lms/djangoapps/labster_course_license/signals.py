"""
This file contains signals for labster_course_license app.
"""
from django.dispatch.dispatcher import receiver
from xmodule.modulestore.django import SignalHandler


@receiver(SignalHandler.course_published)
def on_course_publish(sender, course_key, **kwargs):  # pylint: disable=unused-argument
    """
    Will receive a delegated 'course_published' signal
    and kick off a celery task to update the course access structure.
    """
    # prevent from circular import
    from .tasks import update_course_access

    update_course_access.delay(unicode(course_key))
