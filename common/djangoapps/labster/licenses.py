from django.contrib.auth.models import User

from courseware.courses import get_course
from opaque_keys.edx.locations import SlashSeparatedCourseKey

from labster.models import LabsterUserLicense


def get_course_license_count(course_id):
    """
    return total, used
    """
    total = used = available = 0

    course_id = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    course = get_course(course_id)
    total = course.max_student_enrollments_allowed
    used = LabsterUserLicense.course_licenses_count(course_id)

    if total:
        available = total - used

    return {
        'used': used,
        'available': available,
        'total': total,
    }


def get_user_licenses(course_id):
    user_licenses = LabsterUserLicense.get_for_course(course_id)
    emails = [each.email for each in user_licenses]
    users = User.objects.filter(email__in=emails).prefetch_related('profile')
    name_by_emails = {user.email: user.profile.name for user in users}

    return [
        {
            'course_id': user_license.course_id.to_deprecated_string(),
            'email': user_license.email,
            'name': name_by_emails.get(user_license.email, ''),
        } for user_license in user_licenses
    ]
