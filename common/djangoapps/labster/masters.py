from lxml import etree
import requests

from labster.models import QuizBlock, Problem, Answer
from labster.quiz_blocks import QUIZ_BLOCK_S3_PATH
from labster.utils import get_hashed_text


def create_quizblock_from_tree(lab, tree):
    for child in tree.getchildren():
        if child.tag != 'QuizBlock':
            continue

        element_id = child.attrib.get('Id').strip()

        quiz_block, _ = QuizBlock.objects.get_or_create(lab=lab, element_id=element_id)
        quiz_block.is_active = True
        quiz_block.save()

        create_problem_from_tree(quiz_block, child)


def create_problem_from_tree(quiz_block, tree):
    for child in tree.getchildren():
        if child.tag != 'Quiz':
            continue

        element_id = child.attrib.get('Id').strip()
        problem, _ = Problem.objects.get_or_create(
            quiz_block=quiz_block, element_id=element_id)

        problem.is_active = True
        problem.sentence = child.attrib.get('Sentence', '')
        problem.correct_message = child.attrib.get('CorrectMessage', '')
        problem.wrong_message = child.attrib.get('WrongMessage', '')
        problem.no_score = child.attrib.get('NoScore') == 'true'

        try:
            max_attempts = int(child.attrib.get('MaxAttempts'))
        except:
            max_attempts = None

        problem.max_attempts = max_attempts
        problem.randomize_option_order = child.attrib.get('RandomizeOptionOrder') != 'false'
        problem.save()

        create_answer_from_tree(problem, child)


def create_answer_from_tree(problem, tree):
    for options in tree.getchildren():
        if options.tag != 'Options':
            continue

        for option in options.getchildren():
            if option.tag != 'Option':
                continue

            text = option.attrib.get('Sentence')
            if not text:
                continue

            hashed_text = get_hashed_text(text)

            answer, _ = Answer.objects.get_or_create(
                problem=problem, hashed_text=hashed_text)

            answer.is_correct = option.attrib.get('IsCorrectAnswer') == 'true'
            answer.is_active = True
            answer.text = text.encode('utf-8')
            answer.save()


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
    quizblock_xml = QUIZ_BLOCK_S3_PATH.format(lab.final_quiz_block_file)
    response = requests.get(quizblock_xml)
    assert response.status_code == 200, "missing quizblocks xml"

    qb_tree = etree.fromstring(response.content)
    create_quizblock_from_tree(lab, qb_tree)
