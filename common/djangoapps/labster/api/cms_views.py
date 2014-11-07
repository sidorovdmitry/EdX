from django.http import Http404
from django.utils import timezone

from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from labster.edx_bridge import duplicate_course, unregister_course
from labster.models import Lab


def get_course_meta(user):
    org = "LabsterX"
    number = user.email.replace('@', '.').upper()
    run = timezone.now().strftime("%Y_%m")

    return org, number, run


class CourseDuplicate(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    def post(self, request, *args, **kwargs):
        response_data = {}

        source = request.DATA.get('source')
        target = source
        extra_fields = {
            'invitation_only': True,
            'max_student_enrollments_allowed': 3,
            'labster_license': True,
        }
        scheme = 'https' if request.is_secure() else 'http'
        course = duplicate_course(source, target, request.user, extra_fields,
                                  http_protocol=scheme)

        unregister_course(request.user, source)

        response_data = {'course_id': str(course.id)}
        return Response(response_data)


class CourseDuplicateFromLabs(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    def post(self, request, *args, **kwargs):
        """
        [
            {'lab_id': 1, 'license_count': 10},
            {'lab_id': 2, 'license_count': 10},
            {'lab_id': 3, 'license_count': 10},
        ]
        """

        labs = request.DATA.get('labs', [])
        labs_by_id = {str(each['lab_id']): each for each in labs}
        lab_ids = labs_by_id.keys()

        labs = Lab.objects.filter(id__in=lab_ids)

        course_ids = []
        for lab in labs:
            lab_data = labs_by_id[str(lab.id)]
            license_count = int(lab_data['license_count'])
            extra_fields = {
                'invitation_only': True,
                'max_student_enrollments_allowed': license_count,
                'labster_license': True,
            }

            scheme = 'https' if request.is_secure() else 'http'
            source = target = lab.demo_course_id.to_deprecated_string()
            course = duplicate_course(source, target, request.user, extra_fields,
                                    http_protocol=scheme)

            course_ids.append(str(course.id))

        response_data = {'courses': course_ids}
        return Response(response_data)
