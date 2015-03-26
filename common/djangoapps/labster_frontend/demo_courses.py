from labster.courses import get_demo_courses
from labster_frontend.models import DemoCourse


def populate_demo_courses():
    courses = get_demo_courses()
    for course in courses:
        course_id = course.id.to_deprecated_string()
        try:
            obj = DemoCourse.objects.get(course_id=course_id)
        except DemoCourse.DoesNotExist:
            obj = DemoCourse(course_id=course_id)
            obj.save()
