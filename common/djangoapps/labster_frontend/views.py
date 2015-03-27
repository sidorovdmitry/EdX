from django.http import Http404

from courseware.views import course_about

from labster_frontend.models import DemoCourse


def demo_course(request, slug):
    try:
        demo_course = DemoCourse.objects.get(slug__iexact=slug)
    except:
        raise Http404
    return course_about(request, demo_course.course_id.to_deprecated_string())
