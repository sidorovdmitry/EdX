"""
API related to providing field overrides for individual students.  This is used
by the individual custom courses feature.
"""
import logging
from courseware.field_overrides import FieldOverrideProvider
from labster_course_license.models import LicensedCoursewareItems, CourseLicense
from labster_course_license.utils import get_block_course_key


log = logging.getLogger(__name__)


class LicensedBlocksOverrideProvider(FieldOverrideProvider):
    """
    A concrete implementation of
    :class:`~courseware.field_overrides.FieldOverrideProvider` which allows for
    overrides to be made on a per user basis.
    """
    def get(self, block, name, default):
        """
        Just call the get_override_for_ccx method if there is a ccx
        """
        if name != 'visible_to_staff_only':
            return default
        course_key = get_block_course_key(block)
        if course_key is None:
            msg = "Unable to get course id when calculating ccx overide for block type %r"
            log.error(msg, type(block))

        return is_visible_to_staff_only(course_key, block, default)

    @classmethod
    def enabled_for(cls, course):
        """
        CCX field overrides are enabled per-course

        protect against missing attributes
        """
        return getattr(course, 'enable_ccx', False)


def is_visible_to_staff_only(course_key, block, default):
    """
    Show block if its licensed simulations intersect with course simulations.
    """
    try:
        location = block.location.to_block_locator()
    except AttributeError:
        location = block.location

    try:
        course_locator = course_key.to_course_locator()
    except AttributeError:
        course_locator = course_key

    try:
        # List of actual simulations in the block (chapter, seq, vertical).
        item = LicensedCoursewareItems.objects.get(block=location)
        # List of licensed simulations in the course
        course_license = CourseLicense.objects.get(course_id=course_locator)
    except LicensedCoursewareItems.DoesNotExist, CourseLicense.DoesNotExist:
        return default

    available_simulations = set(course_license.simulations)
    actual_simulations = set(item.simulations)
    if len(actual_simulations.intersection(available_simulations)):
        return default
    else:
        return True
