import csv

from django.core.management.base import BaseCommand
from django.utils import timezone

from labster.models import Scale, Category, Problem, Answer, QuizBlock, Lab
from labster.utils import get_hashed_text


def create_answer(problem, text, is_correct, order, score=None):
    if not text:
        return None

    hashed_text = get_hashed_text(text)
    try:
        answer = Answer.objects.get(hashed_text=hashed_text, problem=problem)
    except Answer.DoesNotExist:
        answer = Answer(hashed_text=hashed_text, problem=problem, text=text)

    answer.is_active = True
    answer.order = order
    answer.is_correct = is_correct
    answer.score = score
    answer.save()

    return answer


class Command(BaseCommand):

    def handle(self, *args, **options):

        lab_id = 71
        Lab.objects.get(id=lab_id)

        path = "data/adaptive_2015.csv"
        with open(path, 'rb') as csv_file:
            reader = csv.DictReader(csv_file)

            for problem_order, row in enumerate(reader):
                quiz_block_id = row['Quiz Block'].strip()
                try:
                    quiz_block = QuizBlock.objects.get(lab_id=lab_id, element_id=quiz_block_id)
                except QuizBlock.DoesNotExist:
                    quiz_block = QuizBlock(lab_id=lab_id, element_id=quiz_block_id)

                quiz_block.is_active = True
                quiz_block.save()

                item_number = row['POST TEST'].strip()
                print item_number

                try:
                    problem = Problem.objects.get(element_id=item_number, quiz_block=quiz_block)
                except Problem.DoesNotExist:
                    problem = Problem(element_id=item_number, quiz_block=quiz_block)

                question = row['Question'].strip()
                scale = row['Scale'].strip()

                problem.is_active = True
                problem.sentence = question
                problem.hashed_sentence = get_hashed_text(question)
                problem.order = problem_order
                problem.randomize_option_order = False
                problem.no_score = True
                problem.is_adaptive = True

                if 'labsterim' in scale:
                    problem.sentence = """<p>{}</p><p><img src="{}" /></p>""".format(question, scale)

                problem.save()

                if scale:
                    if 'Question_' not in scale:
                        try:
                            category = Category.objects.get(name__iexact=scale)
                        except Category.DoesNotExist:
                            category = Category.objects.create(name=scale)

                        problem.categories.clear()
                        problem.categories.add(category)

                correct_answer = row['Correct answer'].strip()
                base_answer_order = 0
                if correct_answer and correct_answer != 'N/A':
                    base_answer_order = 1
                    create_answer(problem, correct_answer, True, base_answer_order)

                create_answer(problem, row['Possible Answer 1'].strip(), False, base_answer_order + 1)
                create_answer(problem, row['Possible Answer 2'].strip(), False, base_answer_order + 2)
                create_answer(problem, row['Possible Answer 3'].strip(), False, base_answer_order + 3)
                create_answer(problem, row['Possible Answer 4'].strip(), False, base_answer_order + 4)
                create_answer(problem, row['Possible Answer 5'].strip(), False, base_answer_order + 5)
                create_answer(problem, row['Possible Answer 6'].strip(), False, base_answer_order + 6)
                create_answer(problem, row['Possible Answer 7'].strip(), False, base_answer_order + 7)
                create_answer(problem, row['Possible Answer 8'].strip(), False, base_answer_order + 8)
