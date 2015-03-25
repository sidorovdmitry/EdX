import six
import json
from collections import defaultdict

try:
    import cStringIO.StringIO as StringIO
except ImportError:
    StringIO = six.StringIO

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render, render_to_response
from django.utils import timezone
from django.utils.xmlutils import SimplerXMLGenerator
from django.views.generic import View, DetailView

from rest_framework.authtoken.models import Token

from courseware.courses import get_course_by_id
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from student.models import CourseEnrollment

from labster.models import LabProxy, UserSave, UserAttempt, Problem, UserAnswer, QuizBlock
from labster.models import LabsterCourseLicense, LabsterUserLicense
from labster.reports import get_attempts_and_answers


API_PREFIX = getattr(settings, 'LABSTER_UNITY_API_PREFIX', '')


def invalid_browser(request):
    template_name = 'labster/lms/invalid_browser.html'
    context = {
    }
    return render_to_response(template_name, context)


def demo_lab(request):
    template_name = 'labster/lms/demo_lab.html'
    context = {
    }
    return render(request, template_name, context)


class XMLView(View):
    charset = 'utf-8'
    root_name = 'Root'

    def get_root_attributes(self, request):
        return {}

    def insert_children(self, xml):
        pass

    def get(self, request, *args, **kwargs):

        stream = StringIO()
        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()
        xml.startElement(self.root_name, self.get_root_attributes(request))

        self.insert_children(xml)

        xml.endElement(self.root_name)
        xml.endDocument()

        response = HttpResponse(stream.getvalue())
        response['Content-Type'] = 'text/xml; charset={}'.format(self.charset)

        return response


class LabProxyXMLView(XMLView):

    def get_lab_proxy(self):
        from opaque_keys.edx.locations import SlashSeparatedCourseKey

        course_id = self.kwargs.get('course_id')
        section = self.kwargs.get('section')

        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        location = "i4x://{}/{}/sequential/{}".format(
            course_key.org, course_key.course, section)

        lab_proxy = LabProxy.objects.get(location=location)
        return lab_proxy


class SettingsXml(LabProxyXMLView):
    root_name = 'Settings'

    def get_engine_xml(self, lab_proxy, user):
        engine_xml = "Engine_Cytogenetics.xml"

        if lab_proxy.lab.engine_xml:
            engine_xml = lab_proxy.lab.engine_xml

        user_save_file_url = self.get_user_save_file_url(lab_proxy, user)
        if user_save_file_url:
            engine_xml = user_save_file_url

        return engine_xml

    def get_user_save_file_url(self, lab_proxy, user):
        engine_xml = ''

        # check if user has finished
        # if user's not finished the game, try to fetch the save file
        user_attempt = UserAttempt.objects.latest_for_user(lab_proxy, user)
        if not user_attempt or user_attempt.is_finished:
            return ''

        # check for save game
        try:
            user_save = UserSave.objects.get(lab_proxy=lab_proxy, user=user)
        except UserSave.DoesNotExist:
            pass
        else:
            if user_save.save_file:
                engine_xml = user_save.save_file.url

        return engine_xml

    def get_user(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            ref_url = request.META.get('HTTP_REFERER')
            if not ref_url:
                raise Http404
            _, token = ref_url.split('?token=')
            token = Token.objects.get(key=token)
            user = token.user
        return user

    def get_root_attributes(self, request):
        lab_proxy = self.get_lab_proxy()
        user = self.get_user(request)

        engine_xml = self.get_engine_xml(lab_proxy, user)
        url_prefix = lab_proxy.lab.xml_url_prefix
        language = lab_proxy.language if lab_proxy.language else 'en'

        return {
            'EngineXML': engine_xml,
            'NavigationMode': "Classic",
            'CameraMode': "Standard",
            'InputMode': "Mouse",
            'HandMode': "Hand",
            'URLPrefix': url_prefix,
            'Language': language,
        }


class PlatformXml(LabProxyXMLView):
    root_name = 'Settings'

    def get_root_attributes(self, request):
        return {
            'Id': "ModularLab",
            'Version': "1",
            'Title': "Labster",
            'LoaderAsset': "Loading",
            'LoaderScene': "Loading",
        }


class ServerXml(LabProxyXMLView):
    root_name = 'Server'

    def get_root_attributes(self, request):
        return {
            'Url': API_PREFIX,
        }

    def insert_children(self, xml):
        lab_proxy = self.get_lab_proxy()

        save_game = reverse('labster-api:save', args=[lab_proxy.id])
        player_start_end = reverse('labster-api:play', args=[lab_proxy.id])
        quiz_block = reverse('labster-api:questions', args=[lab_proxy.id])
        # graph_data = reverse('labster-api:graph_data')

        if lab_proxy.lab.use_quiz_blocks:
            quiz_statistic = reverse('labster-api:answer', args=[lab_proxy.id])
        else:
            quiz_statistic = reverse('labster-api:create-log', args=[lab_proxy.id, 'quiz_statistic'])

        game_progress = reverse('labster-api:create-log', args=[lab_proxy.id, 'game_progress'])
        device_info = reverse('labster-api:create-log', args=[lab_proxy.id, 'device_info'])
        send_email = reverse('labster-api:create-log', args=[lab_proxy.id, 'send_email'])

        # wiki = reverse('labster-api:wiki-article', args=['replaceme'])
        wiki = "/labster/api/wiki/article/"

        children = [
            {'Id': "GameProgress", 'Path': game_progress},
            {'Id': "DeviceInfo", 'Path': device_info},
            {'Id': "QuizStatistic", 'Path': quiz_statistic},
            {'Id': "SaveGame", 'Path': save_game},
            {'Id': "SendEmail", 'Path': send_email},
            {'Id': "PlayerStartEnd", 'Path': player_start_end},
            {'Id': "Wiki", 'Path': wiki, 'CatchError': "false", 'AllowCache': "true"},
            {'Id': "QuizBlock", 'Path': quiz_block},
            # {'Id': "GraphData", 'Path': graph_data},
        ]

        for child in children:
            xml.startElement('ServerAPI', child)
            xml.endElement('ServerAPI')


class PlayLab(View):

    def get_lab_proxy(self):
        from opaque_keys.edx.locations import SlashSeparatedCourseKey

        course_id = self.kwargs.get('course_id')
        section = self.kwargs.get('section')

        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        location = "i4x://{}/{}/sequential/{}".format(
            course_key.org, course_key.course, section)

        lab_proxy = LabProxy.objects.get(location=location)
        return lab_proxy

    def render(self, request):
        return HttpResponse(1)


class StartNewLab(PlayLab):

    def get_user(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            key = request.GET.get('token')
            if not key:
                return None
            token = Token.objects.get(key=key)
            user = token.user
        return user

    def get(self, request, *args, **kwargs):
        prev_url = request.get_full_path()
        if not request.user.is_authenticated():
            return HttpResponseBadRequest('Missing user')

        lab_proxy = self.get_lab_proxy()

        user = self.get_user(request)
        if not user:
            return HttpResponseBadRequest('Missing user')

        UserAttempt.objects.filter(
            lab_proxy=lab_proxy, user=user, is_finished=False).update(
                is_finished=True, finished_at=timezone.now())

        return self.render(request)


class ContinueLab(PlayLab):

    def get(self, request, *args, **kwargs):
        return self.render(request)


class LabResult(DetailView):
    template_name = "labster/lms/lab_result.html"
    model = LabProxy

    def get_context_data(self, *args, **kwargs):
        context = super(LabResult, self).get_context_data(*args, **kwargs)
        course_id = self.kwargs.get('course_id')
        course = get_course_by_id(SlashSeparatedCourseKey.from_deprecated_string(course_id))
        user = self.request.user
        lab_proxy = context['object']
        attempts = get_attempts_and_answers(lab_proxy, user, latest_only=True)
        headers = ['Question', 'Answer', 'Correct Answer', 'Correct?']

        context.update({
            'attempts': attempts,
            'headers': headers,
            'course': course,
        })
        return context


class AdaptiveTestResult(DetailView):
    template_name = "labster/lms/adaptive_test_result.html"
    model = LabProxy

    def get_cytogenetics_score(self, user, lab_proxy):
        attempt = UserAttempt.objects\
            .filter(user=user, lab_proxy=lab_proxy)\
            .exclude(useranswer=None)\
            .order_by('-created_at')[0]

        # scored
        quiz_block_id = 'QuizblockPreTest'
        quiz_block = QuizBlock.objects.get(lab=lab_proxy.lab, element_id=quiz_block_id)
        problems = Problem.objects\
            .filter(is_active=True, quiz_block=quiz_block)\
            .order_by('order')

        answers = UserAnswer.objects.filter(attempt=attempt, problem__in=problems)
        answers_by_quiz_id = {a.problem.element_id: a for a in answers}
        answered = []

        score = 0
        user_answers = []
        for problem in problems:
            if problem.element_id in answered:
                continue

            answered.append(problem.element_id)
            answer = answers_by_quiz_id.get(problem.element_id)
            if answer:
                user_answers.append(answer)
                if answer.is_correct:
                    score += 1

        score = score * 100 / problems.count()
        return score, user_answers

    def get_psychological_scores(self, user, lab_proxy):
        attempt = UserAttempt.objects\
            .filter(user=user, lab_proxy=lab_proxy)\
            .exclude(useranswer=None)\
            .order_by('-created_at')[0]

        NEG_SCORES = {
            'Completely disagree': 5,
            'Disagree': 4,
            'Neither agree nor disagree': 3,
            'Agree': 2,
            'Completely agree': 1,
        }

        POS_SCORES = {
            'Completely disagree': 1,
            'Disagree': 2,
            'Neither agree nor disagree': 3,
            'Agree': 4,
            'Completely agree': 5,
        }

        quiz_block_ids = ['QuizBlockSection1', 'QuizBlockSection2', 'QuizBlockSection3', 'QuizBlockSection4']
        quiz_blocks = QuizBlock.objects.filter(lab=lab_proxy.lab, element_id__in=quiz_block_ids)
        problems = Problem.objects.filter(is_active=True, quiz_block__in=quiz_blocks)
        if not problems.exists():
            return None

        answers = UserAnswer.objects.filter(attempt=attempt, problem__in=problems)

        raw_scores = defaultdict(int)
        scores = defaultdict(int)
        counts = defaultdict(int)
        for answer in answers:
            category = answer.problem.categories.values_list('name', flat=True)[0]
            category = category.upper().replace(' ', '_').replace('-', '_')

            counts[category] += 1
            if answer.problem.direction_for_scoring == 'negative':
                raw_scores[category] += NEG_SCORES[answer.answer_string]
            else:
                raw_scores[category] += POS_SCORES[answer.answer_string]

        for category, score in raw_scores.items():
            scores[category] = score * 100 / (counts[category] * 5)
        return scores

    def get_context_data(self, *args, **kwargs):
        context = super(AdaptiveTestResult, self).get_context_data(*args, **kwargs)
        course_id = self.kwargs.get('course_id')
        course = get_course_by_id(SlashSeparatedCourseKey.from_deprecated_string(course_id))
        user = self.request.user
        lab_proxy = context['object']

        psy_scores = self.get_psychological_scores(user, lab_proxy)
        score, user_answers = self.get_cytogenetics_score(user, lab_proxy)

        context.update({
            'user_answers': user_answers,
            'course': course,
            'score': score,
            'psy_scores': psy_scores,
            'show_result': lab_proxy.lab.id == 44,
        })
        return context


class EnrollStudentVoucher(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        email = data.get('email')
        license_id = data.get('license_id')
        try:
            user = User.objects.get(email=email)
        except:
            return HttpResponseBadRequest('invalid email or license_id')

        course_licenses = LabsterCourseLicense.objects.filter(license_id=license_id)
        for course_license in course_licenses:
            record, _ = CourseEnrollment.objects.get_or_create(
                user=user, course_id=course_license.course_id)
            record.is_active = True
            record.save()

            user_license, _ = LabsterUserLicense.objects.get_or_create(
                email=email,
                course_id=course_license.course_id)

        return HttpResponse(json.dumps({'success': True}))


class EnrollStudentCourse(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        email = data.get('email')
        course_id = data.get('course_id')
        try:
            user = User.objects.get(email=email)
        except:
            return HttpResponseBadRequest('invalid email or course id')

        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)

        # enroll student to the course
        record, _ = CourseEnrollment.objects.get_or_create(
            user=user, course_id=course_key)
        record.is_active = True
        record.save()

        user_license, _ = LabsterUserLicense.objects.get_or_create(
            email=email, course_id=course_key)

        return HttpResponse(json.dumps({'success': True}))


settings_xml = SettingsXml.as_view()
server_xml = ServerXml.as_view()
platform_xml = PlatformXml.as_view()
start_new_lab = StartNewLab.as_view()
continue_lab = ContinueLab.as_view()
lab_result = login_required(LabResult.as_view())
adaptive_test_result = login_required(AdaptiveTestResult.as_view())
enroll_student_voucher = login_required(EnrollStudentVoucher.as_view())
enroll_student_course = login_required(EnrollStudentCourse.as_view())
