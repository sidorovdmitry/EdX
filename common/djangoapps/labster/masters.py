from lxml import etree
import requests

from django.utils import timezone

from labster.models import Lab, QuizBlock, Problem, Answer
from labster.utils import get_hashed_text


def create_quizblock_from_tree(lab, tree):
    order = 1

    QuizBlock.objects.filter(lab=lab).update(is_active=False)
    for child in tree.getchildren():
        if child.tag != 'QuizBlock':
            continue

        element_id = child.attrib.get('Id').strip()

        quiz_block, _ = QuizBlock.objects.get_or_create(lab=lab, element_id=element_id)
        quiz_block.is_active = True
        quiz_block.order = order
        quiz_block.save()

        create_problem_from_tree(quiz_block, child)
        order += 1


def create_problem_from_tree(quiz_block, tree):
    order = 1

    Problem.objects.filter(quiz_block=quiz_block).update(is_active=False)
    for child in tree.getchildren():
        if child.tag != 'Quiz':
            continue

        element_id = child.attrib.get('Id').strip()
        problem, _ = Problem.objects.get_or_create(
            quiz_block=quiz_block, element_id=element_id)

        problem.is_adaptive = quiz_block.element_id in ['QuizblockPreTest', 'QuizblockPostTest']
        problem.is_active = True
        problem.sentence = child.attrib.get('Sentence', '').strip()
        problem.hashed_sentence = get_hashed_text(problem.sentence)
        problem.correct_message = child.attrib.get('CorrectMessage', '')
        problem.wrong_message = child.attrib.get('WrongMessage', '')
        problem.no_score = child.attrib.get('NoScore') == 'true'
        problem.current_conv_popup_id = child.attrib.get('CurrentConvPopupId', '')
        problem.image_id = child.attrib.get('ImageId', '')
        problem.read_more_url = child.attrib.get('ReadMoreUrl', '')
        problem.quiz_group = child.attrib.get('QuizGroup', '')
        problem.is_explorable = child.attrib.get('IsExplorable') == 'true'
        problem.order = order

        try:
            max_attempts = int(child.attrib.get('MaxAttempts'))
        except:
            max_attempts = None

        problem.max_attempts = max_attempts
        problem.randomize_option_order = child.attrib.get('RandomizeOptionOrder') != 'false'
        problem.save()

        create_answer_from_tree(problem, child)
        order += 1


def create_answer_from_tree(problem, tree):
    order = 1
    Answer.objects.filter(problem=problem).update(is_active=False)
    Answer.objects.filter(problem=problem).update(is_correct=False)
    for options in tree.getchildren():
        if options.tag != 'Options':
            continue

        for option in options.getchildren():
            if option.tag != 'Option':
                continue

            text = option.attrib.get('Sentence', '').strip()
            if not text:
                continue

            hashed_text = get_hashed_text(text)

            answer, _ = Answer.objects.get_or_create(
                problem=problem, hashed_text=hashed_text)

            answer.is_correct = answer.is_correct or option.attrib.get('IsCorrectAnswer') == 'true'
            answer.is_active = True
            answer.text = text.encode('utf-8')
            answer.order = order
            answer.save()
            order += 1


def fetch_quizblocks(lab):
    """
    Fetch this lab's quizblocks
    This will implicitly fetch problems and answers as well
    """

    # set all inactive
    QuizBlock.objects.filter(lab=lab).update(is_active=False)
    Problem.objects.filter(quiz_block__lab=lab).update(is_active=False)
    Answer.objects.filter(problem__quiz_block__lab=lab).update(is_active=False)

    # quizblocks
    quizblock_xml = lab.quiz_block_file_url
    response = requests.get(quizblock_xml)
    assert response.status_code == 200, "missing quizblocks xml"

    qb_tree = etree.fromstring(response.content)
    create_quizblock_from_tree(lab, qb_tree)

    Lab.objects.filter(id=lab.id).update(
        quiz_block_last_updated=timezone.now())


def fetch_labs_as_json():
    labs = Lab.objects.order_by('name')
    labs_json = [lab.to_json() for lab in labs]
    return labs_json


def get_quiz_block_as_platform_xml(quiz_block):
    attrib = {
        'Id': quiz_block.element_id,
    }

    if quiz_block.time_limit:
        attrib['TimeLimit'] = str(quiz_block.time_limit)

    if quiz_block.can_skip:
        attrib['CanSkip'] = "true"

    quiz_block_el = etree.Element('QuizBlock', attrib)

    # fetch active problems
    problems = Problem.objects.filter(
        quiz_block=quiz_block, is_active=True)

    for problem in problems:
        problem_xml = get_problem_as_platform_xml(problem)
        quiz_block_el.append(problem_xml)

    return quiz_block_el


def get_problem_as_platform_xml(problem):
    answers = Answer.objects.filter(problem=problem, is_active=True)

    quiz_attrib = {
        'Id': problem.element_id,
        'CorrectMessage': problem.correct_message,
        'WrongMessage': problem.wrong_message,
        'Sentence': problem.sentence,
    }

    extra = {}
    if problem.no_score:
        extra['NoScore'] = "true"
    if problem.max_attempts:
        extra['MaxAttempts'] = str(problem.max_attempts)
    if problem.current_conv_popup_id:
        extra['CurrentConvPopupId'] = problem.current_conv_popup_id
    if problem.image_id:
        extra['ImageId'] = problem.image_id
    if problem.read_more_url:
        extra['ReadMoreUrl'] = problem.read_more_url
    if problem.quiz_group:
        extra['QuizGroup'] = problem.quiz_group

    if not problem.randomize_option_order:
        extra['RandomizeOptionOrder'] = "false"

    if problem.is_explorable:
        extra['IsExplorable'] = "true"

    quiz_attrib.update(extra)

    quiz_el = etree.Element('Quiz', quiz_attrib)
    options = etree.SubElement(quiz_el, 'Options')

    for answer in answers:
        if not answer.text:
            continue

        answer_attrib = {'Sentence': answer.text}
        if answer.is_correct:
            answer_attrib['IsCorrectAnswer'] = "true"

        etree.SubElement(options, 'Option', **answer_attrib)

    return quiz_el


def get_problem(lab_proxy, quiz_id=None, question=None):
    problem = None

    if quiz_id:
        try:
            problem = Problem.objects.get(
                is_active=True,
                quiz_block__lab=lab_proxy.lab,
                element_id=quiz_id)
        except Problem.DoesNotExist:
            problem = None

    elif question:
        try:
            hashed = get_hashed_text(question)
            problem = Problem.objects.get(
                is_active=True,
                quiz_block__lab=lab_proxy.lab,
                hashed_sentence=hashed)
        except Problem.DoesNotExist:
            problem = None

    return problem
