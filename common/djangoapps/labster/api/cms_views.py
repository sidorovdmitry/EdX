from django.utils import timezone

from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from labster.backoffice.views import get_payment
from labster.courses import duplicate_course
from labster.edx_bridge import unregister_course
from labster.models import Lab
from labster.models import LabsterCourseLicense


def get_course_meta(user):
    org = "LabsterX"
    number = user.email.replace('@', '.').upper()
    run = timezone.now().strftime("%Y_%m")

    return org, number, run


def get_duplicate_course(source, username):
    _, rest = source.split('/', 1)
    result = "{}/{}".format(username, rest)
    return result


class CourseDuplicate(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    def post(self, request, *args, **kwargs):
        response_data = {}

        source = request.DATA.get('source')
        target = get_duplicate_course(source, request.user.username)
        extra_fields = {
            'invitation_only': True,
            'max_student_enrollments_allowed': 3,
            'labster_license': True,
        }

        unregister_course(request.user, source)
        course = duplicate_course(source, target, request.user, extra_fields)

        response_data = {'course_id': str(course.id)}
        return Response(response_data)


def get_all_lab_ids():
    def has_demo(lab):
        if lab.demo_course_id:
            return True
        return False

    labs = Lab.objects.all()
    lab_ids = [lab.id for lab in labs if has_demo(lab)]

    return lab_ids


class CourseDuplicateFromLabs(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    def post(self, request, *args, **kwargs):
        labs = request.DATA.get('labs', [])
        payment_id = request.DATA.get('payment_id')
        token = request.DATA.get('token')

        payment = get_payment(payment_id, token)
        labs_by_id = {}
        for payment_product in payment['payment_products']:

            if payment_product['product_external_id']:
                lab_id = payment_product['product_external_id']
                license_id = payment_product['license_id']
                if not lab_id or not license_id:
                    continue

                labs_by_id[lab_id] = payment_product
            else:
                # handle all labs and package labs
                lab_ids = payment_product['list_products_id']
                if not lab_ids:
                    continue
                for lab_id in lab_ids:
                    labs_by_id[str(lab_id)] = payment_product

        lab_ids = labs_by_id.keys()

        labs = Lab.objects.filter(id__in=lab_ids)

        course_ids = []
        for lab in labs:
            lab_data = labs_by_id[str(lab.id)]
            license_count = int(lab_data['item_count'])
            license_id = int(lab_data['license_id'])

            extra_fields = {
                'invitation_only': True,
                'max_student_enrollments_allowed': license_count,
                'labster_license': True,
            }

            source = target = lab.demo_course_id.to_deprecated_string()
            course = duplicate_course(source, target, request.user, extra_fields)

            if course:
                course_ids.append(str(course.id))

                LabsterCourseLicense.objects.create(
                    user=request.user, course_id=course.id, license_id=license_id)

        response_data = {'courses': course_ids}
        return Response(response_data)
