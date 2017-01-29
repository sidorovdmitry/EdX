"""
API related to providing field overrides for individual students.  This is used
by the individual custom courses feature.
"""
import json
import logging

from courseware.field_overrides import FieldOverrideProvider
from ccx.overrides import get_current_ccx

from lms.djangoapps.labster_course_license.models import LicensedCoursewareItems
from lms.djangoapps.labster_course_license.utils import get_block_course_key


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
        ccx = None
        course_key = get_block_course_key(block)
        if course_key is None:
            msg = "Unable to get course id when calculating ccx overide for block type %r"
            log.error(msg, type(block))
        else:
            ccx = get_current_ccx(course_key)
        if ccx:
            return is_visible_to_staff_only(block)
        return default

    @classmethod
    def enabled_for(cls, course):
        """CCX field overrides are enabled per-course

        protect against missing attributes
        """
        return getattr(course, 'enable_ccx', False)


def is_visible_to_staff_only(block):
    courseware_item = LicensedCoursewareItems.objects.get(block=block.location.block_id)
    print(courseware_item)
