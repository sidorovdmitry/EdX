import operator

from django.db.models import Q

from courseware.courses import get_course
from opaque_keys.edx.locations import SlashSeparatedCourseKey

from labster_search.models import LabKeyword
from labster_search.utils import uniqify


def get_course_ids_from_keywords(keywords):
    """
    Fetches course_ids based on keyword
    It consists of 2 parts:
        the first one is it tries to fetch course_ids with all keywords (AND)
        then it tries to fetch course_ids with any keywords (OR)
    """
    if not keywords:
        return []

    keyword_list = keywords.split()
    primary_course_ids = []
    and_course_ids = []
    or_course_ids = []

    results = LabKeyword.objects.all()

    # primary
    primary_results = results.filter(keyword__icontains=keywords)
    primary_course_ids = primary_results.values_list('course_id', flat=True)

    # and
    and_filters = reduce(operator.and_, (Q(keyword__icontains=keyword) for keyword in keyword_list))
    and_results = results.filter(and_filters)
    and_course_ids = and_results.values_list('course_id', flat=True)

    if len(keywords) > 1:
        # or
        or_filters = reduce(operator.or_, (Q(keyword__icontains=keyword) for keyword in keyword_list))
        or_results = results.filter(or_filters)
        or_course_ids = or_results.values_list('course_id', flat=True)

    course_ids = list(primary_course_ids) + list(and_course_ids) + list(or_course_ids)
    course_ids = uniqify(course_ids)
    return course_ids


def get_courses_from_keywords(keywords):
    if not keywords:
        return []

    course_ids = get_course_ids_from_keywords(keywords)
    course_ids = filter(None, course_ids)
    courses = []
    for course_id in course_ids:
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        try:
            courses.append(get_course(course_key))
        except (ValueError, AssertionError):
            continue

    return courses
