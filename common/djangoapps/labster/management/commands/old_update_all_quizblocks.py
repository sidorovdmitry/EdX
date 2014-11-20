from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from courseware.courses import get_course_by_id
from opaque_keys.edx.keys import UsageKey
from xmodule.modulestore.django import modulestore

from labster.constants import ADMIN_USER_ID
from labster.quiz_blocks import update_course_lab, validate_lab_proxy
from labster.models import LabProxy


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.get(id=ADMIN_USER_ID)

        lab_proxies = LabProxy.all_objects.all()
        for lab_proxy in lab_proxies:
            course, section, sub_section = validate_lab_proxy(lab_proxy)
            if not course:
                continue

            self.stdout.write('{} - {} - {}\n'.format(
                lab_proxy.id, course.id, lab_proxy.lab.name))

            update_course_lab(
                user, course, section.display_name, sub_section.display_name,
                command=self, force_update=True)
