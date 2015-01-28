from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from contentstore.utils import delete_course_and_groups
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from student.roles import CourseInstructorRole, CourseStaffRole
from student.models import UserProfile, CourseAccessRole, CourseEnrollment
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import modulestore

from labster.models import Lab, LabsterUser


ORG = "VUCVestegnen"
UNIVERSITY = "VUC Vestegnen"


def create_course_id(course_id):
    return course_id.replace('LabsterX', ORG)


def course_key_str(course_key):
    return course_key.to_deprecated_string()


def get_demo_course_ids():
    return [lab.demo_course_id for lab in Lab.objects.all() if lab.demo_course_id]


def course_key_from_str(arg):
    try:
        return CourseKey.from_string(arg)
    except InvalidKeyError:
        return SlashSeparatedCourseKey.from_deprecated_string(arg)


class Command(BaseCommand):

    def prepare(self):
        email = "it@vucv.dk"
        password = email
        name = "Carsten Pedersen"
        username = "CarstenPedersen"

        try:
            user = User.objects.get(email=email)
        except:
            user = User(email=email)
        user.username = username
        user.is_active = True
        user.set_password(password)
        user.save()

        labster_user, _ = LabsterUser.objects.get_or_create(user=user)
        labster_user.user_type = LabsterUser.USER_TYPE_TEACHER
        labster_user.user_school_level = LabsterUser.USER_HIGH_SCHOOL
        labster_user.save()

        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        user_profile.name = name
        user_profile.save()

        return User.objects.get(id=user.id)

    def create_courses(self):
        user = self.prepare()
        demo_course_ids = map(course_key_str, get_demo_course_ids())
        new_course_ids = map(create_course_id, demo_course_ids)

        for source, target in zip(demo_course_ids, new_course_ids):
            source_course_id = course_key_from_str(source)
            dest_course_id = course_key_from_str(target)

            mstore = modulestore()
            delete_course_and_groups(dest_course_id, ModuleStoreEnum.UserID.mgmt_command)

            print("Cloning course {0} to {1}".format(source_course_id, dest_course_id))

            try:
                with mstore.bulk_operations(dest_course_id):
                    if mstore.clone_course(source_course_id, dest_course_id, ModuleStoreEnum.UserID.mgmt_command):
                        print("copying User permissions...")
                        # purposely avoids auth.add_user b/c it doesn't have a caller to authorize
                        CourseInstructorRole(dest_course_id).add_users(
                            *CourseInstructorRole(source_course_id).users_with_role()
                        )
                        CourseStaffRole(dest_course_id).add_users(
                            *CourseStaffRole(source_course_id).users_with_role()
                        )
            except:
                continue

            CourseAccessRole.objects.get_or_create(
                user=user,
                org=ORG,
                course_id=dest_course_id,
                role='staff')

            CourseAccessRole.objects.get_or_create(
                user=user,
                org=ORG,
                course_id=dest_course_id,
                role='instructor')

            CourseEnrollment.objects.get_or_create(
                user=user, course_id=dest_course_id)

    def handle(self, *args, **options):
        self.create_courses()
