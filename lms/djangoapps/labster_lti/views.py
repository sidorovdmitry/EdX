from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404

from xmodule.modulestore.django import modulestore

from labster.courses import get_lab_proxy_from_course_key
from labster_frontend.models import get_lab_from_slug, get_course_key_from_slug
from labster_lti.models import LTIUser


def iframe(request, lab_slug, provider):
    lab = get_lab_from_slug(slug=lab_slug.strip())
    course_key = get_course_key_from_slug(slug=lab_slug.strip())
    lab_proxy = get_lab_proxy_from_course_key(course_key)
    if not lab or not course_key or not lab_proxy:
        raise Http404

    external_user_id = request.GET.get('external_user_id')
    if not external_user_id:
        return HttpResponseBadRequest('missing external_user_id')

    lti_user = LTIUser.create(external_user_id, provider)
    course = modulestore().get_course(course_key)
    request.session['lti_user_id'] = lti_user.id

    context = {
        'course': course,
        'lab': lab,
        'lti_user': lti_user,
        'lab_url': reverse('labster_lti_lab', args=[lab_slug]),
    }

    template_name = 'labster_lti/iframe.html'
    return render(request, template_name, context)


def lab(request, lab_slug):
    lab = get_lab_from_slug(slug=lab_slug.strip())
    course_key = get_course_key_from_slug(slug=lab_slug.strip())
    lab_proxy = get_lab_proxy_from_course_key(course_key)
    if not lab or not course_key or not lab_proxy:
        raise Http404

    continue_from_save = request.GET.get('continue') == 'yes'

    lti_user = get_object_or_404(LTIUser, id=request.session.get('lti_user_id'))
    context = {
        'lti_user': lti_user,
        'lab': lab,
        'token_key': lti_user.user.labster_user.token_key,
    }

    template_name = 'labster_lti/lab.html'
    return render(request, template_name, context)
