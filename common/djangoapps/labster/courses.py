import re

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from student.models import UserProfile, CourseAccessRole, CourseEnrollment
from student.roles import CourseInstructorRole, CourseStaffRole
from xmodule.course_module import CourseDescriptor
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import modulestore

from labster.models import Lab, LabsterUser
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


def get_org(user):
    labster_user = LabsterUser.objects.get(user=user)
    if labster_user.organization_name:
        org = labster_user.organization_name
    else:
        org = user.username

    pattern = re.compile('[\W_]+', re.UNICODE)
    org = pattern.sub('', org)
    return org


def duplicate_course(source, target, user, fields=None):
    from contentstore.utils import delete_course_and_groups

    org = target.split('/')[0]
    source_org = source.split('/')[0]
    target_org = org

    if source_org == target_org:
        target = target.replace(org, get_org(user))

    source_course_id = course_key_from_str(source)
    dest_course_id = course_key_from_str(target)

    mstore = modulestore()
    delete_course_and_groups(dest_course_id, ModuleStoreEnum.UserID.mgmt_command)

    try:
        with mstore.bulk_operations(dest_course_id):
            if mstore.clone_course(source_course_id, dest_course_id,
                                   ModuleStoreEnum.UserID.mgmt_command):
                pass
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

    course_fields = {
        'labster_demo': False,
        'is_browsable': False,
        'invitation_only': True,
        'max_student_enrollments_allowed': 3,
        'labster_license': True,
    }
    if fields:
        course_fields.update(fields)

    course = mstore.get_course(dest_course_id)
    for key, value in course_fields.items():
        setattr(course, key, value)

    mstore.update_item(course, user.id)

    return course


def duplicate_multiple_courses(user, license_count, all_labs, labs, org):

    if all_labs:
        demo_course_ids = map(course_key_str, get_demo_course_ids())
    else:
        demo_course_ids = unicode_to_str(labs)

    new_course_ids = []
    for course_id in demo_course_ids:
        new_course_ids.append(create_course_id(org, course_id))

    results = []
    for source, target in zip(demo_course_ids, new_course_ids):
        dest_course = duplicate_course(
            source,
            target,
            user,
            fields={'max_student_enrollments_allowed': license_count},
        )

        results.append(dest_course.id.to_deprecated_string())
    return results


def get_demo_courses():
    courses = modulestore().get_courses()
    courses = [c for c in courses if isinstance(c, CourseDescriptor)]
    courses = [course for course in courses if course.labster_demo and course.is_browsable]

    return courses


def create_course_id(org, course_id):
    return course_id.replace('LabsterX', org)


def get_demo_course_ids():
    return [lab.demo_course_id for lab in Lab.objects.all() if lab.demo_course_id]


def get_demo_course_ids_list(demo_course_ids):
    return [lab.demo_course_id for lab in Lab.objects.filter(demo_course_id__in=demo_course_ids) if lab.demo_course_id]


def course_key_from_str(arg):
    try:
        return CourseKey.from_string(arg)
    except InvalidKeyError:
        return SlashSeparatedCourseKey.from_deprecated_string(arg)


def course_key_str(course_key):
    return course_key.to_deprecated_string()


def unicode_to_str(labs):
    return [lab.encode("utf-8") for lab in labs]
