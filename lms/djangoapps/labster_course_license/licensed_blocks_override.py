"""
API related to providing field overrides for individual students.  This is used
by the individual custom courses feature.
"""
import json
import logging

from courseware.field_overrides import FieldOverrideProvider
from ccx.overrides import get_current_ccx

from ccx_keys.locator import CCXLocator

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

        print('=====', block.location)
        for i in LicensedCoursewareItems.objects.all():
            print('-', i.block)
        for i in CourseLicense.objects.all():
            print('~', i.course_id)
        try:
            # List of actual simulations in the block (chapter, seq, vertical).
            items = LicensedCoursewareItems.objects.get(block=block.location)
        except LicensedCoursewareItems.DoesNotExist:
            return default
        print('items', items)

        try:
            # List of actual simulations in the block (chapter, seq, vertical).
            ccx_license = CourseLicense.objects.get(course_id=course_key)
        except CourseLicense.DoesNotExist:
            return default
        print('ccx_license', ccx_license)

        available_simulations = set(ccx_license.simulations.values_list('code', flat=True))
        actual_simulations = set(items.simulations.values_list('code', flat=True))
        print(block.display_name)
        print('license', available_simulations)
        print('MC', actual_simulations)
        if actual_simulations.intersection(available_simulations):
            # chapter 1 (sim 1 sim2 sim3): visible True
            #     seq (sim 1 sim2) visible True
            #         v 1 sim 1 visible False
            #         v 2 sim 2 visible True
            #         text blocks ???
            #     seq (sim 3) visible False
            #         v 3 sim 3 visible False
            #
            #  License sim 2 sim 4

            return False
        return default

    @classmethod
    def enabled_for(cls, course):
        """
        CCX field overrides are enabled per-course

        protect against missing attributes
        """
        return getattr(course, 'enable_ccx', False)


def is_visible_to_staff_only(block, default):
    """
    Returns visible_to_staff_only value for block or default value if block has no licensed simulations.
    """
    try:
        courseware_item = LicensedCoursewareItems.objects.get(block=block.location.block_id)
    except LicensedCoursewareItems.DoesNotExist:
        return default

    licensed_simulations = json.loads(courseware_item.licensed_simulations)
    if licensed_simulations:
        return default
    else:
        return True
