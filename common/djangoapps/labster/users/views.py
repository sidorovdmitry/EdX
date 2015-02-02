from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from opaque_keys.edx.locations import SlashSeparatedCourseKey
from student.models import CourseEnrollment

from rest_framework.authtoken.models import Token


def login_by_token(request):
    user_id = request.POST.get('user_id')
    course_id = request.POST.get('course_id')
    token_key = request.POST.get('token_key')
    next_url = request.POST.get('next', '/')

    try:
        token = Token.objects.get(key=token_key, user_id=user_id)
    except Token.DoesNotExist:
        token = None

    if token:
        user = authenticate(key=token.key)
        if user and user.is_active:
            login(request, user)

        if course_id:
            user = User.objects.get(id=user.id)
            course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
            CourseEnrollment.enroll(user, course_key)

    return HttpResponseRedirect(next_url)
