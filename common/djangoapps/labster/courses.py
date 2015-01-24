from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xmodule.modulestore.django import modulestore

from labster.models import Lab
from labster_search.models import LabKeyword


def get_popular_courses(courses_id):
    '''
    Returns a list of most popular courses
    '''
    courses = []

    for course_id in courses_id:
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        course = modulestore().get_course(course_key)
        if course:
            courses.append(course)

    return courses


def get_primary_keywords(course_id, count=10):
    # lab
    try:
        lab = Lab.objects.get(demo_course_id=course_id)
    except Lab.DoesNotExist:
        return []

    lab_keywords = LabKeyword.objects\
        .filter(lab=lab, keyword_type=LabKeyword.KEYWORD_PRIMARY)\
        .order_by('-rank')
    return lab_keywords[:count]
