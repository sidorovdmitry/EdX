from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django_future.csrf import ensure_csrf_cookie

from edxmako.shortcuts import render_to_response
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from student.models import CourseEnrollment, CourseEnrollmentAllowed, UserProfile

from rest_framework.authtoken.models import Token

from labster.models import LabsterUser


def sync_user(user):
    try:
        labster_user = LabsterUser.objects.get(user=user)
        user_profile = UserProfile.objects.get(user=user)
        create_user(user, user_profile.name, labster_user, format='json')
    except LabsterUser.DoesNotExist:
        pass


def enroll_user(user):
    # Teacher could enroll student that doesn't exist yet.
    # So if the student registers, enroll him/her to the courses

    ceas = CourseEnrollmentAllowed.objects.filter(email=user.email)
    for cea in ceas:
        if cea.auto_enroll:
            CourseEnrollment.enroll(user, cea.course_id)


def login_by_token(request):
    user_id = request.POST.get('user_id')
    user_type = request.POST.get('user_type')
    course_id = request.POST.get('course_id')
    token_key = request.POST.get('token_key')
    next_url = request.POST.get('next', '/')
    is_demo_course = request.POST.get('is_demo_course', "true") # from javascript it sends string

    if not token_key or not user_id:
        return HttpResponseRedirect(next_url)

    try:
        token = Token.objects.get(key=token_key, user_id=user_id)
    except Token.DoesNotExist:
        token = None

    if token:
        user = authenticate(key=token.key)
        if user and user.is_active:
            login(request, user)
            enroll_user(user)

        if course_id :
            if (is_demo_course == "false" and int(user_type) == LabsterUser.USER_TYPE_STUDENT) or int(user_type) == LabsterUser.USER_TYPE_TEACHER:
                # if it's an open course e.g. adaptive course then enroll them all otherwise just enroll the teacher
                user = User.objects.get(id=user.id)
                course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
                CourseEnrollment.enroll(user, course_key)

                next_url = reverse('info', args=[course_key.to_deprecated_string()])
                return HttpResponseRedirect(next_url)

    return HttpResponseRedirect(next_url)


@ensure_csrf_cookie
def activate_user_email(request, activation_key):
    try:
        labster_user = LabsterUser.objects.get(email_activation_key=activation_key)
    except LabsterUser.DoesNotExist:
        raise Http404

    try:
        profile = UserProfile.objects.get(user=labster_user.user)
    except UserProfile.DoesNotExist:
        raise Http404

    user_logged_in = request.user.is_authenticated()
    labster_user.is_email_active = True
    labster_user.save()

    resp = render_to_response(
        "registration/labster_activation_complete.html",
        {
            'user_logged_in': user_logged_in,
            'already_active': False,
            'profile': profile,
        }
    )
    return resp
