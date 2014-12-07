from collections import defaultdict
from lxml import etree
import csv
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
from labster.models import LabProxy, ProblemProxy, LabProxyData, UserAttempt, UserAnswer
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


def generate_lab_proxy_data(
    lab_proxy, quiz_blocks=None, quiz_ids=None, filters=None,
    file_name=None,
    process_score=False,
    score_file_name=None):

    ## row
    # QuizBlock, QuizID, Email, User ID, Question, Correct Answer, Answer,
    # Is Correct, Completion Time

    stream = StringIO()
    writer = csv.writer(stream)
    headers = [
        'Quiz ID',
        'Email',
        'User ID',
        'Question',
        'Correct Answer',
        'Answer',
        'Is Correct',
        'Completion Time',
        'Number of Attempts',
        'QuizBlock',
        'Attempt Group',
    ]

    writer.writerow(headers)

    user_attempts = UserAttempt.objects.filter(lab_proxy=lab_proxy)
    if filters:
        user_attempts = user_attempts.filter(**filters)

    user_attempts = user_attempts.exclude(user__email__endswith='labster.com')
    user_attempts = user_attempts.exclude(user__email__endswith='liv.it')
    user_attempts = user_attempts.exclude(user__email='mitsurudy@gmail.com')

    user_attempts = user_attempts.order_by('user__id', 'created_at')
    attempt_groups = defaultdict(int)
    scores = []

    for user_attempt in user_attempts:
        attempt_groups[user_attempt.user_id] += 1

        user = user_attempt.user
        unique_id = user.profile.unique_id
        if not unique_id:
            unique_id = user.id

        score = {
            'email': user.email,
            'name': user.profile.name.encode('utf-8'),
            'user_id': unique_id.encode('utf-8'),
            'score': 0,
            'raw_score': 0,
            'attempt_count': 0,
        }

        user_answers = UserAnswer.objects.filter(attempt=user_attempt)
        for user_answer in user_answers:
            problem = user_answer.problem
            quiz_block = problem.quiz_block

            if quiz_blocks and quiz_block.element_id not in quiz_blocks:
                continue

            if quiz_ids and problem.element_id not in quiz_ids:
                continue

            score['attempt_count'] += 1

            is_correct = ""
            if not problem.no_score:
                is_correct = "yes" if user_answer.is_correct else "no"

            if user_answer.is_correct:
                score['raw_score'] += 1

            row = [
                problem.element_id,
                user.email,
                unique_id.encode('utf-8'),
                user_answer.question.encode('utf-8'),
                user_answer.correct_answer.encode('utf-8'),
                user_answer.answer_string.encode('utf-8'),
                is_correct,
                user_answer.completion_time,
                user_answer.attempt_count,
                quiz_block.element_id,
                "{}-{}".format(user.email, attempt_groups[user.id]),
            ]

            writer.writerow(row)

        if score['attempt_count']:
            score['score'] = 100 * score['raw_score'] / score['attempt_count']
            scores.append(score)

    now = timezone.now()
    if not file_name:
        file_name = 'lp_{}_{}.csv'.format(lab_proxy.id, now.strftime('%Y%m%d%H%M%S'))
    csv_file = ContentFile(stream.getvalue(), file_name)
    lab_proxy_data = LabProxyData(lab_proxy=lab_proxy)
    lab_proxy_data.data_file.save(file_name, csv_file, save=False)

    if process_score:
        score_stream = export_score(scores)
        score_file_name = score_file_name
        score_file = ContentFile(score_stream.getvalue(), score_file_name)
        lab_proxy_data.score_file.save(score_file_name, score_file, save=False)

    lab_proxy_data.save()


def export_score(scores):
    stream = StringIO()
    writer = csv.writer(stream)

    headers = [
        'User ID',
        'Name',
        'Email',
        'Score',
    ]

    writer.writerow(headers)

    for score in scores:
        row = [
            score['user_id'],
            score['name'],
            score['email'],
            score['score'],
        ]

        writer.writerow(row)

    return stream
