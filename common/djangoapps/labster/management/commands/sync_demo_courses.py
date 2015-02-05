from xmodule.course_module import CourseDescriptor
from xmodule.modulestore.django import modulestore

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.get(id=19)
        courses = modulestore().get_courses()
        courses = [c for c in courses if isinstance(c, CourseDescriptor)]
        for course in courses:
            updated = False

            if course.is_browsable:
                course.labster_demo = True
                updated = True
            elif course.labster_demo:
                course.is_browsable = True
                updated = True

            if updated:
                mstore = modulestore()
                mstore.update_item(course, user.id)
