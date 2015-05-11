from django.core.management.base import BaseCommand

from student.models import CourseAccessRole
from student.roles import CourseInstructorRole, CourseStaffRole


class Command(BaseCommand):

    def handle(self, *args, **options):
        cars = CourseAccessRole.objects.all()
        for car in cars:
            user = car.user
            course_key = car.course_id

            if car.role == 'staff':
                CourseStaffRole(course_key).add_users(user)
            if car.role == 'instructor':
                CourseInstructorRole(course_key).add_users(user)
