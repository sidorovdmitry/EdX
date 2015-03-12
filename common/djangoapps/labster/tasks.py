from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail

from django_rq import job

from labster.courses import duplicate_multiple_courses


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
def duplicate_courses(user_id, license_count, all_labs, labs, org):
    user = User.objects.get(id=user_id)
    course_ids = duplicate_multiple_courses(user, license_count, all_labs, labs, org)
    send_completed_email(user, course_ids)
