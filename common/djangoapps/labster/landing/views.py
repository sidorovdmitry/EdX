from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect
from django_future.csrf import ensure_csrf_cookie
from django.contrib.auth.models import User, AnonymousUser
from django.db.models import Count

from edxmako.shortcuts import render_to_response

from util.cache import cache_if_anonymous
from courseware.courses import get_courses, sort_by_announcement

from labster.models import UserAttempt, Lab
from labster.courses import get_popular_courses_labster


@ensure_csrf_cookie
@cache_if_anonymous
def index(request, user=AnonymousUser()):
    '''
    Redirects to main page -- info page if user authenticated, or marketing if not
    '''

    if settings.COURSEWARE_ENABLED and request.user.is_authenticated():
        return redirect(reverse('dashboard'))

    if settings.FEATURES.get('AUTH_USE_CERTIFICATES'):
        from external_auth.views import ssl_login
        # Set next URL to dashboard if it isn't set to avoid
        # caching a redirect to / that causes a redirect loop on logout
        if not request.GET.get('next'):
            req_new = request.GET.copy()
            req_new['next'] = reverse('dashboard')
            request.GET = req_new
        return ssl_login(request)

    # The course selection work is done in courseware.courses.
    domain = settings.FEATURES.get('FORCE_UNIVERSITY_DOMAIN')  # normally False
    # do explicit check, because domain=None is valid
    if domain is False:
        domain = request.META.get('HTTP_HOST')

    courses = get_courses(user, domain=domain)
    courses = sort_by_announcement(courses)

    # get 5 popular labs
    user_attempts = UserAttempt.objects.all().values('lab_proxy__lab').annotate(total=Count('lab_proxy__lab')).order_by('-total')
    labs_id = []

    # get the lab foreign key
    for lab_id in user_attempts:
        labs_id.append(lab_id['lab_proxy__lab'])

    # get course_id
    # courses_id = Lab.objects.filter(id__in=labs_id).values_list('demo_course_id', flat=True)
    courses_id = Lab.objects.filter(id__in=labs_id).values_list('demo_course_id', flat=True)
    list_courses_id = []
    for course_id in courses_id:
        if not course_id:
            continue
        list_courses_id.append(course_id)

    # get courses based on course id
    popular_labs = get_popular_courses_labster(courses_id)

    context = {
        'courses': courses,
        'popular_labs': popular_labs,
    }

    return render_to_response('labster_landing.html', context)


@ensure_csrf_cookie
@cache_if_anonymous
def courses(request, user=AnonymousUser()):
    """
    Render the "find courses" page. If the marketing site is enabled, redirect
    to that. Otherwise, if subdomain branding is on, this is the university
    profile page. Otherwise, it's the edX courseware.views.courses page
    """

    if not settings.FEATURES.get('COURSES_ARE_BROWSABLE'):
        raise Http404

    # The course selection work is done in courseware.courses.
    domain = settings.FEATURES.get('FORCE_UNIVERSITY_DOMAIN')  # normally False
    # do explicit check, because domain=None is valid
    if domain is False:
        domain = request.META.get('HTTP_HOST')

    courses = get_courses(user, domain=domain)
    courses = sort_by_announcement(courses)

    # get 5 popular labs
    user_attempts = UserAttempt.objects.all().values('lab_proxy__lab').annotate(total=Count('lab_proxy__lab')).order_by('-total')
    labs_id = []

    # get the lab foreign key
    for lab_id in user_attempts:
        labs_id.append(lab_id['lab_proxy__lab'])

    # get course_id
    # courses_id = Lab.objects.filter(id__in=labs_id).values_list('demo_course_id', flat=True)
    courses_id = Lab.objects.filter(id__in=labs_id).values_list('demo_course_id', flat=True)
    list_courses_id = []
    for course_id in courses_id:
        if not course_id:
            continue
        list_courses_id.append(course_id)

    # get courses based on course id
    popular_labs = get_popular_courses_labster(courses_id)

    context = {
        'courses': courses,
        'popular_labs': popular_labs,
    }

    return render_to_response('courseware/labster_courses.html', context)
