from lxml import etree
import requests

from django.core.management.base import BaseCommand

from labster.models import Lab, QuizBlock, Problem, Answer
from labster.quiz_blocks import QUIZ_BLOCK_S3_PATH
from labster.utils import get_hashed_text


class Command(BaseCommand):

    def handle(self, *args, **options):
        # set all inactive
        QuizBlock.objects.all().update(is_active=False)
        Problem.objects.all().update(is_active=False)
        Answer.objects.all().update(is_active=False)

        labs = Lab.objects.order_by('id')
        total = labs.count()

        for index, lab in enumerate(labs, start=1):
            self.stdout.write("{}/{}: {}\n".format(
                index, total, lab.name))

            # quizblocks
            quizblock_xml = QUIZ_BLOCK_S3_PATH.format(lab.final_quiz_block_file)
            response = requests.get(quizblock_xml)
            assert response.status_code == 200, "missing quizblocks xml"

            qb_tree = etree.fromstring(response.content)
            for qb_child in qb_tree.getchildren():
                if qb_child.tag != 'QuizBlock':
                    continue

                element_id = qb_child.attrib.get('Id').strip()

                quiz_block, _ = QuizBlock.objects.get_or_create(lab=lab, element_id=element_id)
                quiz_block.is_active = True
                quiz_block.save()

                for problem_child in qb_child.getchildren():
                    if qb_child.tag != 'Quiz':
                        continue

                    element_id = problem_child.attrib.get('Id').strip()
                    problem, _ = Problem.objects.get_or_create(
                        quiz_block=quiz_block, element_id=element_id)

                    problem.is_active = True
                    problem.sentence = problem_child.attrib.get('Sentence', '')
                    problem.correct_message = problem_child.attrib.get('CorrectMessage', '')
                    problem.wrong_message = problem_child.attrib.get('WrongMessage', '')
                    problem.no_score = problem_child.attrib.get('NoScore') == 'true'

                    try:
                        max_attempts = int(problem_child.attrib.get('MaxAttempts'))
                    except:
                        max_attempts = None

                    problem.max_attempts = max_attempts
                    problem.randomize_option_order = problem_child.attrib.get('RandomizeOptionOrder') != 'false'
                    problem.save()

                    for options in problem_child.getchildren():
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
