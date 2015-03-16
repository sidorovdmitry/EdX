from labster.backoffice.views import get_backoffice_urls

from edxmako.shortcuts import render_to_response

from django.conf import settings
from django.contrib.auth.decorators import login_required

from student.models import UserProfile

from labster.models import LabsterUser


@login_required
def home(request):
    template_name = 'labster/student_voucher_code.html'
    user_profile = UserProfile.objects.get(user=request.user)
    labster_user = LabsterUser.objects.get(user=request.user)

    token = bo_user['token']
    backoffice = {
        'user_id': bo_user['id'],
        'user_country': user_profile.country,
        'user_edu_level': labster_user.user_school_level
    }

    backoffice_urls = get_backoffice_urls()
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    context = {
        'token': token,
        'backoffice': backoffice,
        'backoffice_urls': backoffice_urls,
        'stripe_publishable_key': stripe_publishable_key,
    }
    return render_to_response(template_name, context)
