import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404

from edxmako.shortcuts import render_to_response

from student.models import UserProfile

from labster.models import LabsterUser

from opaque_keys.edx.locations import SlashSeparatedCourseKey

from courseware.courses import get_course_by_id

from labster.backoffice.views import create_user, get_backoffice_urls
from labster.utils import country_code_from_ip


def get_lab_id(course_id):
    course = get_course_by_id(SlashSeparatedCourseKey.from_deprecated_string(course_id))
    lab_id = None
    for section in course.get_children():
        for sub_section in section.get_children():
            if sub_section.lab_id:
                lab_id = sub_section.lab_id
    return lab_id, course


@login_required
def home(request, course_id):
    template_name = 'labster/student_license.html'
    user_profile = UserProfile.objects.get(user=request.user)
    labster_user = LabsterUser.objects.get(user=request.user)
    bo_user = create_user(request.user, user_profile.name, labster_user, format='json')
    ip = request.META.get('REMOTE_ADDR', None)
    if ip:
        country = country_code_from_ip(ip)
    else:
        country = ""

    user_edu_level = "hs" if user_profile.level_of_education == "hs" else "univ"
    token = bo_user['token']
    backoffice = {
        'user_id': bo_user['id'],
        'user_country': user_profile.country,
        'user_edu_level': user_edu_level
    }

    backoffice_urls = get_backoffice_urls()
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    lab_id, course = get_lab_id(course_id)
    context = {
        'token': token,
        'backoffice': backoffice,
        'backoffice_urls': backoffice_urls,
        'stripe_publishable_key': stripe_publishable_key,
        'lab_id': lab_id,
        'course' : course,
        'course_id': course_id,
        'country': country,
    }
    return render_to_response(template_name, context)
