from django.contrib.auth.models import User

from django_rq import job

from labster.courses import duplicate_multiple_courses


@job
def duplicate_courses(user_id, license_count, all_labs, labs, org):
    user = User.objects.get(id=user_id)
    duplicate_multiple_courses(user, license_count, all_labs, labs, org)
