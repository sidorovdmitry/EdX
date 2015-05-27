from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render

from xmodule.modulestore.django import modulestore

from labster_frontend.models import get_lab_from_slug, get_course_key_from_slug
from labster_lti.models import LTIUser


def iframe(request, lab_slug, provider):
    lab = get_lab_from_slug(slug=lab_slug.strip())
    course_key = get_course_key_from_slug(slug=lab_slug.strip())
    if not lab or not course_key:
        raise Http404

    external_user_id = request.GET.get('external_user_id')
    if not external_user_id:
        return HttpResponseBadRequest('missing external_user_id')

    lti_user = LTIUser.create(external_user_id, provider)
    course = modulestore().get_course(course_key)

    context = {
        'course': course,
        'lab': lab,
        'lti_user': lti_user,
    }

    template_name = 'labster_lti/iframe.html'
    return render(request, template_name, context)
