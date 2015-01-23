from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xmodule.modulestore.django import modulestore


def get_popular_courses(courses_id, max=6):
    '''
    Returns a list of most popular courses
    '''
    courses = []

    for course_id in courses_id[:max]:
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        course = modulestore().get_course(course_key, depth=1)
        if course:
            courses.append(course)

    return courses
