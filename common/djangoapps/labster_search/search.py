import operator

from django.db.models import Q

from courseware.courses import get_course

from labster.models import Lab
from labster_search.models import LabKeyword
from labster_search.utils import uniqify


def get_labs_from_keywords(keywords):
    """
    Fetches labs based on keyword
    It consists of 2 parts:
        the first one is it tries to fetch labs with all keywords (AND)
        then it tries to fetch lab with any keywords (OR)
    """
    if not keywords:
        return []

    keyword_list = keywords.split()
    primary_lab_ids = []
    and_lab_ids = []
    or_lab_ids = []

    results = LabKeyword.objects.all()

    # primary
    primary_results = results.filter(keyword__icontains=keywords)
    primary_lab_ids = primary_results.values_list('lab_id', flat=True)

    # and
    and_filters = reduce(operator.and_, (Q(keyword__icontains=keyword) for keyword in keyword_list))
    and_results = results.filter(and_filters)
    and_lab_ids = and_results.values_list('lab_id', flat=True)

    if len(keywords) > 1:
        # or
        or_filters = reduce(operator.or_, (Q(keyword__icontains=keyword) for keyword in keyword_list))
        or_results = results.filter(or_filters)
        or_lab_ids = or_results.values_list('lab_id', flat=True)

    lab_ids = list(primary_lab_ids) + list(and_lab_ids) + list(or_lab_ids)
    lab_ids = uniqify(lab_ids)
    labs = Lab.objects.in_bulk(lab_ids)
    ordered_labs = [labs[lab_id] for lab_id in lab_ids]
    return ordered_labs


def get_courses_from_keywords(keywords):
    if not keywords:
        return []

    labs = get_labs_from_keywords(keywords)
    course_ids = [lab.demo_course_id for lab in labs if lab.demo_course_id]
    courses = []
    for course_id in course_ids:
        try:
            courses.append(get_course(course_id))
        except ValueError:
            continue

    return courses
