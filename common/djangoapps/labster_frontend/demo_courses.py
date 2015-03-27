from django.core.urlresolvers import reverse

from opaque_keys.edx.locations import SlashSeparatedCourseKey

from labster.courses import get_demo_courses, get_lab_by_course_id
from labster_frontend.models import DemoCourse


def populate_demo_courses():
    courses = get_demo_courses()
    for course in courses:
        course_id = course.id.to_deprecated_string()
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        lab = get_lab_by_course_id(course_key)
        try:
            obj = DemoCourse.objects.get(course_id=course_key)
        except DemoCourse.DoesNotExist:
            obj = DemoCourse(course_id=course_key)
        obj.lab = lab
        obj.save()


def labsterify_courses(courses):
    """
    fetch labster demo course link if available
    """

    for course in courses:
        try:
            demo_course = DemoCourse.objects.get(course_id=course.id)
        except DemoCourse.DoesNotExist:
            slug = ''
        else:
            slug = demo_course.slug

        if slug:
            url = reverse('labster_demo_course', args=[demo_course.slug])
        else:
            url = reverse('about_course', args=[course.id.to_deprecated_string()])
        course.labster_demo_course_url = url

    return courses
