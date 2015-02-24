from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from student.models import CourseAccessRole, CourseEnrollment
from student.roles import CourseInstructorRole, CourseStaffRole
from xmodule.course_module import CourseDescriptor
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import modulestore

from labster.models import Lab
from labster_search.models import LabKeyword


def get_popular_courses(courses_id):
    '''
    Returns a list of most popular courses
    '''
    courses = []

    for course_id in courses_id:
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        course = modulestore().get_course(course_key)
        if course:
            courses.append(course)

    return courses


def get_primary_keywords(course_id):
    # lab
    try:
        lab = Lab.objects.get(demo_course_id=course_id)
    except Lab.DoesNotExist:
        return []

    lab_keywords = LabKeyword.objects\
        .filter(lab=lab, keyword_type=LabKeyword.KEYWORD_PRIMARY)\
        .order_by('-rank')
    return lab_keywords


def course_key_from_str(arg):
    try:
        return CourseKey.from_string(arg)
    except InvalidKeyError:
        return SlashSeparatedCourseKey.from_deprecated_string(arg)


def duplicate_course(source, target, user, fields=None):
    org = target.split('/')[0]
    source_org = source.split('/')[0]
    target_org = org

    if source_org == target_org:
        target = target.replace(org, user.username)

    source_course_id = course_key_from_str(source)
    dest_course_id = course_key_from_str(target)

    mstore = modulestore()
    # delete_course_and_groups(dest_course_id, ModuleStoreEnum.UserID.mgmt_command)

    # 'invitation_only': True,
    # 'max_student_enrollments_allowed': license_count,
    # 'labster_license': True,

    try:
        with mstore.bulk_operations(dest_course_id):
            if mstore.clone_course(source_course_id, dest_course_id, ModuleStoreEnum.UserID.mgmt_command):
                # purposely avoids auth.add_user b/c it doesn't have a caller to authorize
                CourseInstructorRole(dest_course_id).add_users(
                    *CourseInstructorRole(source_course_id).users_with_role()
                )
                CourseStaffRole(dest_course_id).add_users(
                    *CourseStaffRole(source_course_id).users_with_role()
                )
    except:
        return None

    course = mstore.get_course(dest_course_id)

    if fields:
        for key, value in fields.items():
            setattr(course, key, value)

        mstore.update_item(course, user.id)

    CourseInstructorRole(dest_course_id).add_users(user)
    CourseStaffRole(dest_course_id).add_users(user)

    CourseEnrollment.objects.get_or_create(
        user=user, course_id=dest_course_id)

    fields = {
        'labster_demo': False,
        'is_browsable': False,
        'invitation_only': True,
        'max_student_enrollments_allowed': 3,
        'labster_license': True,
    }
    course = mstore.get_course(dest_course_id)
    for key, value in fields.items():
        setattr(course, key, value)

    mstore.update_item(course, user.id)

    return course


def get_demo_courses():
    courses = modulestore().get_courses()
    courses = [c for c in courses if isinstance(c, CourseDescriptor)]
    courses = [course for course in courses if course.labster_demo and course.is_browsable]

    return courses
