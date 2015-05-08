from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone

from django_rq import job

from labster.courses import duplicate_multiple_courses, course_key_from_str
from labster.models import LabsterCourseLicense

from labster_backoffice.models import License, Voucher

COMPLETED_EMAIL_BODY = """
Hello,

We're happy to inform you the courses you bought are ready.
Go to dashboard (http://www.labster.com/dashboard) to check it.

Best Regards,
Labster
"""


def send_completed_email(user, course_ids):
    from_email = settings.DEFAULT_FROM_EMAIL
    to_emails = [
        user.email,
    ]
    subject = "Your {} is Ready".format("Courses" if len(course_ids) > 1 else "Course")
    body = COMPLETED_EMAIL_BODY.strip()
    send_mail(subject, body, from_email, to_emails)


@job
def duplicate_courses(user_id, license_count, all_labs, labs, org, voucher_code=None, request_user_id=None):
    user = User.objects.get(id=user_id)
    course_ids = duplicate_multiple_courses(user, license_count, all_labs, labs, org)
    if request_user_id:
        request_user = User.objects.get(id=request_user_id)
    else:
        request_user = user

     # if there is voucher code, then create license for the teacher and create labster course license data
    if voucher_code:
        voucher = Voucher.objects.get(id=voucher_code)

        # create license
        date_end_license = timezone.now() + relativedelta(weeks=+voucher.week_subscription)
        license = License(user=user, voucher_code=voucher_code, date_bought=timezone.now(), date_end_license=date_end_license,
            is_active=True, item_count=license_count, item_used=0)
        license.save()

        # create course license data
        for item in course_ids:
            course_id = course_key_from_str(item)
            LabsterCourseLicense.objects.get_or_create(
                user_id=user.id,
                license_id=license.id,
                course_id=course_id)

    send_completed_email(request_user, course_ids)
