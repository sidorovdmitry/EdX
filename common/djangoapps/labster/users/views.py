from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from opaque_keys.edx.locations import SlashSeparatedCourseKey
from student.models import CourseEnrollment, UserProfile

from rest_framework.authtoken.models import Token

from labster.models import LabsterUser

def sync_user(user):
    try:
        labster_user = LabsterUser.objects.get(user=user)
        user_profile = UserProfile.objects.get(user=user)
        create_user(user, user_profile.name, labster_user, format='json')
    except LabsterUser.DoesNotExist:
        pass

def login_by_token(request):
    user_id = request.POST.get('user_id')
    user_type = request.POST.get('user_type')
    course_id = request.POST.get('course_id')
    token_key = request.POST.get('token_key')
    next_url = request.POST.get('next', '/')

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

        if int(user_type) == LabsterUser.USER_TYPE_TEACHER and course_id:
            # only enroll the teacher
            user = User.objects.get(id=user.id)
            course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
            CourseEnrollment.enroll(user, course_key)

    return HttpResponseRedirect(next_url)
