import csv

from lxml import etree
import six
try:
    import cStringIO.StringIO as StringIO
except ImportError:
    StringIO = six.StringIO

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils import timezone

from xmodule.modulestore.django import modulestore

from labster.masters import get_problem_as_platform_xml, get_quiz_block_as_platform_xml
from labster.models import LabProxy, ProblemProxy, LabProxyData
from labster.models import Lab, QuizBlock, Problem, UserAnswer
from labster.parsers.problem_parsers import QuizParser
from labster.quiz_blocks import create_xblock, update_problem, validate_lab_proxy
from labster.utils import get_hashed_text


USER_ID = 19  # kriwil@gmail.com


def prepare_lab(lab, location):
    user = User.objects.get(id=USER_ID)

    lab_proxy, _ = LabProxy.objects.get_or_create(
        lab=lab, location=location)

    lab_proxy.is_active = True
    lab_proxy.save()

    # quizblocks
    quiz_blocks = QuizBlock.objects.filter(lab=lab, is_active=True)
    for quiz_block in quiz_blocks:
        # create unit
        unit = create_unit_from_quiz_block(user, quiz_block, lab_proxy.location)

        problems = Problem.objects.filter(quiz_block=quiz_block, is_active=True)
        for problem in problems:

            # create component
            component = create_component_from_problem(
                user, lab_proxy, problem, unit.location)

            component = modulestore().get_item(component.location)
            modulestore().publish(component.location, user.id)

        unit = modulestore().get_item(unit.location)
        modulestore().publish(unit.location, user.id)


def prepare_lab_from_lab_id(lab_id, location):
    lab = Lab.objects.get(id=lab_id)
    return prepare_lab(lab, location)


def create_unit_from_quiz_block(user, quiz_block, location):
    name = quiz_block.element_id
    unit = create_xblock(user, 'vertical', location, name=name)
    return unit


def get_or_create_problem_proxy(lab_proxy, problem, location):
    problem_proxy, _ = ProblemProxy.objects.get_or_create(
        lab_proxy=lab_proxy, problem=problem, location=location)

    problem_proxy.is_active = True
    problem_proxy.save()

    return problem_proxy


def create_component_from_problem(user, lab_proxy, problem, location):
    name = problem.element_id
    extra_post = {'boilerplate': "multiplechoice.yaml"}
    quiz_block = problem.quiz_block

    component = create_xblock(
        user, 'problem', location.to_deprecated_string(), extra_post=extra_post)

    platform_xml = get_problem_as_platform_xml(problem)
    quiz_parser = QuizParser(platform_xml)
    edx_xml = quiz_parser.parsed_as_string

    update_problem(
        user,
        component,
        data=edx_xml,
        name=component.name,
        platform_xml=etree.tostring(platform_xml, pretty_print=True),
        correct_index=quiz_parser.correct_index,
        correct_answer=quiz_parser.correct_answer,
    )

    get_or_create_problem_proxy(lab_proxy, problem, component.location)

    return component


def sync_lab_proxy(lab_proxy):
    user = User.objects.get(id=USER_ID)

    # get course
    course, section, sub_section = validate_lab_proxy(lab_proxy)
    if not course:
        return

    # delete all units
    for unit in sub_section.get_children():
        modulestore().delete_item(unit.location, user.id)

    prepare_lab(lab_proxy.lab, sub_section.location.to_deprecated_string())


def get_lab_proxy_as_platform_xml(lab_proxy):
    attrib = {'Id': str(lab_proxy.id)}
    lab_proxy_el = etree.Element('Lab', attrib)
    quizblocks_el = etree.SubElement(lab_proxy_el, 'QuizBlocks')

    quiz_blocks = QuizBlock.objects.filter(is_active=True, lab=lab_proxy.lab)
    for quiz_block in quiz_blocks:
        quiz_block_el = get_quiz_block_as_platform_xml(quiz_block)
        quizblocks_el.append(quiz_block_el)

    return lab_proxy_el


def generate_lab_proxy_data(lab_proxy):

    lab = lab_proxy.lab
    quiz_blocks = QuizBlock.objects.filter(is_active=True, lab=lab)

    ## rows
    # QuizBlock, QuizID, Email, User ID, Question, Correct Answer, Answer,
    # Is Correct, Completion Time

    stream = StringIO()
    writer = csv.writer(stream)
    headers = [
        'QuizID',
        'Email',
        'User ID',
        'Question',
        'Correct Answer',
        'Answer',
        'Is Correct',
        'Completion Time',
        'QuizBlock',
    ]

    writer.writerow(headers)

    for quiz_block in quiz_blocks:
        problems = Problem.objects.filter(is_active=True, quiz_block=quiz_block)

        for problem in problems:
            user_answers = UserAnswer.objects.filter(problem=problem)

            for user_answer in user_answers:
                user = user_answer.user

                is_correct = ""
                if not problem.no_score:
                    is_correct = "yes" if user_answer.is_correct else "no"

                rows = [
                    problem.element_id,
                    user.email,
                    user.profile.unique_id,
                    user_answer.question.encode('utf-8'),
                    user_answer.correct_answer.encode('utf-8'),
                    user_answer.answer_string.encode('utf-8'),
                    is_correct,
                    user_answer.completion_time,
                    quiz_block.element_id,
                ]

                writer.writerow(rows)

    now = timezone.now()
    file_name = 'lp_{}_{}.csv'.format(lab_proxy.id, now.strftime('%Y%m%d%H%M%S'))
    csv_file = ContentFile(stream.getvalue(), file_name)
    lab_proxy_data = LabProxyData(lab_proxy=lab_proxy)
    lab_proxy_data.data_file.save(file_name, csv_file, save=False)
    lab_proxy_data.save()
