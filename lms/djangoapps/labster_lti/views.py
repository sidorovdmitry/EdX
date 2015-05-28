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


def settings_xml(request, lab_slug):
    lab = get_lab_from_slug(slug=lab_slug.strip())
    course_key = get_course_key_from_slug(slug=lab_slug.strip())
    if not lab or not course_key:
        raise Http404

    print lab, lab.engine_xml

    context = {
        'url_prefix': lab.get_xml_url_prefix(),
        'engine_xml': lab.engine_xml,
    }
    return render(request, 'labster_lti/settings.xml', context)


def server_xml(request, lab_slug):
    lab = get_lab_from_slug(slug=lab_slug.strip())
    course_key = get_course_key_from_slug(slug=lab_slug.strip())
    lab_proxy = get_lab_proxy_from_course_key(course_key)
    if not lab or not course_key:
        raise Http404

    device_info = reverse('labster-api:create-log', args=[lab_proxy.id, 'device_info'])
    game_progress = reverse('labster-api:create-log', args=[lab_proxy.id, 'game_progress'])
    player_start_end = reverse('labster-api:play', args=[lab_proxy.id])
    quiz_block = reverse('labster-api:questions', args=[lab_proxy.id])
    quiz_statistic = reverse('labster-api:answer', args=[lab_proxy.id])
    save_game = reverse('labster-api:save', args=[lab_proxy.id])
    send_email = reverse('labster-api:create-log', args=[lab_proxy.id, 'send_email'])
    wiki = "/labster/api/wiki/article/"
    api_prefix = getattr(settings, 'LABSTER_UNITY_API_PREFIX', '')

    context = {
        'api_prefix': api_prefix,
        'device_info': device_info,
        'game_progress': game_progress,
        'player_start_end': player_start_end,
        'quiz_block': quiz_block,
        'quiz_statistic': quiz_statistic,
        'save_game': save_game,
        'send_email': send_email,
        'wiki': wiki,
    }
    return render(request, 'labster_lti/server.xml', context)


def platform_xml(request, lab_slug):
    lab = get_lab_from_slug(slug=lab_slug.strip())
    course_key = get_course_key_from_slug(slug=lab_slug.strip())
    if not lab or not course_key:
        raise Http404

    context = {}
    return render(request, 'labster_lti/platform.xml', context)
