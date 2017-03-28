""" Labster Course views. """
import logging

from django.http import Http404
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from ccx_keys.locator import CCXLocator
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from util.json_request import JsonResponse, expect_json
from contentstore.views.course import _create_or_rerun_course
from contentstore.utils import delete_course_and_groups
from xmodule.modulestore.django import modulestore
from xmodule.course_module import CourseDescriptor

from lms.djangoapps.ccx.views import coach_dashboard, _ccx_students_enrrolling_center
from cms.djangoapps.contentstore.utils import add_instructor, remove_all_instructors
from student.roles import CourseCcxCoachRole
from instructor.views.api import _split_input_list
from instructor.enrollment import get_email_params


log = logging.getLogger(__name__)


def set_staff(course_key, emails):
    """
    Sets course staff.
    """
    remove_all_instructors(course_key)
    for email in emails:
        try:
            user = User.objects.get(email=email)
            add_instructor(course_key, user, user)
        except User.DoesNotExist:
            log.info('User with email %s does not exist', email)


def setup_course(course_key, staff=None):
    """
    Updates course staff and licenses.
    """
    if staff is not None:
        set_staff(course_key, staff)


# pylint: disable=unused-argument
@csrf_exempt
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAdminUser,))
@expect_json
def course_handler(request, course_key_string=None):
    """
    **Use Case**
        Get a list of course keys, create, duplicate or delete a course.

    **Example requests**:
        GET /labster/api/course/?org={course_org}&number={course_number}
            /labster/api/course/?org=labster&number=labx

        POST /labster/api/course/
        {
            "org": "labster",
            "number": "LABX1",
            "display_name": "Duplicated Course 1",
            "run": "2015_T2",
            "source_course_key": "course-v1:labster+LABX+2015_T1",
            "staff": ["honor@example.com", "staff@example.com"]
        }

        PUT    /labster/api/course/{course_key}/
               /labster/api/course/course-v1:labster+LABX+2015_T2/
        {
            "staff": ["honor@example.com", "staff@example.com"]
        }

        DELETE /labster/api/course/{course_key}/
               /labster/api/course/course-v1:labster+LABX+2015_T2/

    **Request Parameters**
        * display_name: The public display name for the new course.

        * org: The name of the organization sponsoring the new course.
          Note: No spaces or special characters are allowed.

        * number: The unique number that identifies the new course within the organization.
          Note: No spaces or special characters are allowed.

        * run: The term in which the new course will run.
          Note: No spaces or special characters are allowed.

        * start: The start date for the course.

        * source_course_key(optional): The source course (The course which is duplicated).

        * staff: The list of staff emails to add to the course.
    """
    try:
        if request.method in ('GET', 'POST'):
            if request.method == 'POST':
                store = modulestore()
                with store.default_store('split'):
                    org = request.json.get('org')
                    number = request.json.get('number', request.json.get('course'))
                    run = request.json.get('run')
                    destination_course_key = store.make_course_key(org, number, run)

                response = _create_or_rerun_course(request)
                setup_course(
                    destination_course_key,
                    staff=request.json.get('staff')
                )
                return response

            elif request.method == 'GET':
                filter_by_org = request.GET.get('org')
                filter_by_number = request.GET.get('number')
                courses = modulestore().get_courses(org=filter_by_org)
                courses = filter(lambda c: isinstance(c, CourseDescriptor), courses)

                if filter_by_number:
                    courses = filter(lambda c: c.number.lower() == filter_by_number.lower(), courses)

                return Response([
                    {
                        "display_name": course.display_name,
                        "course_key": unicode(course.location.course_key)
                    } for course in courses
                ])

        elif request.method in ('PUT', 'DELETE'):
            course_key = CourseKey.from_string(course_key_string)
            if request.method == 'PUT':
                setup_course(
                    course_key,
                    staff=request.json.get('staff')
                )
                return Response({"course_key": unicode(course_key)})
            elif request.method == 'DELETE':
                delete_course_and_groups(course_key, request.user.id)
                return Response(status=status.HTTP_204_NO_CONTENT)
    except InvalidKeyError:
        raise Http404


@api_view(['GET'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAdminUser,))
def coach_list_handler(request):
    """
    Returns a list of dicts with information about CCX coaches (full name, email).
    """
    coaches = User.objects.filter(courseaccessrole__role=CourseCcxCoachRole.ROLE).distinct()
    coaches_info = ({
        'full_name': coach.get_full_name(),
        'email': coach.email,
    } for coach in coaches)
    return Response(coaches_info)


@csrf_exempt
@api_view(['POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication))
@permission_classes((IsAdminUser,))
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@coach_dashboard
def ccx_invite(request, course, ccx=None):
    """
    Enroll or unenroll students to CCX by email.
    Requires staff access.

    **Request example**:
        POST /labster/api/course/enroll
        {
            "course_key": "course-v1:labster+LABX+2015_T1",
            "action": "enroll",
            "auto_enroll": true,
            "email_students": false,
            "identifiers": ["honor@example.com", "staff@example.com"]
        }
    Query Parameters:
        - action in ['enroll', 'unenroll']
        - identifiers is string containing a list of emails and/or usernames separated by anything split_input_list can handle.
        - auto_enroll is a boolean (defaults to true)
            If auto_enroll is false, students will be allowed to enroll.
            If auto_enroll is true, students will be enrolled as soon as they register.
        - email_students is a boolean (defaults to false)
            If email_students is true, students will be sent email notification
            If email_students is false, students will not be sent email notification
    """
    if not ccx:
        raise Http404

    action = request.POST.get('action')
    identifiers_raw = request.POST.get('identifiers')
    identifiers = _split_input_list(identifiers_raw)
    auto_enroll = _get_boolean_param(request, 'auto_enroll', deafult=True)
    email_students = _get_boolean_param(request, 'email_students')

    course_key = CCXLocator.from_course_locator(course.id, ccx.id)
    email_params = get_email_params(
        course,
        course_key=course_key,
        auto_enroll=auto_enroll,
        display_name=ccx.display_name,
    )

    _ccx_students_enrrolling_center(action, identifiers, email_students, course_key, email_params)
    log.info(
        "User: %s;\nAction: %s;\nIdentifiers: %s;\nSend email: %s;\nCourse: %s;\nEmail parameters: %s.",
        request.user, action, identifiers, email_students, course_key, email_params
    )
    return Response(status=status.HTTP_200_OK)


def _get_boolean_param(request, param_name, deafult=False):
    """
    Returns the value of the boolean parameter with the given
    name in the POST request. Handles translation from string
    values to boolean values.
    """
    return request.POST.get(param_name, deafult) in ['true', 'True', True]
