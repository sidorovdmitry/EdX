from django.core.management.base import BaseCommand

from labster.models import UserAnswer, Problem


class Command(BaseCommand):

    def handle(self, *args, **options):
        user_answers = UserAnswer.objects.all()
        self.stdout.write("migrating {} data\n".format(user_answers.count()))

        for user_answer in user_answers:
            problem_proxy = user_answer.problem_proxy
            lab_proxy = problem_proxy.lab_proxy

            problem = None
            try:
                problem = Problem.objects.get(
                    lab_proxy=lab_proxy,
                    element_id=user_answer.quiz_id)
            except:
                pass

            if not problem:
                try:
                    problem = Problem.objects.get(
                        lab_proxy=lab_proxy,
                        hashed_sentence=problem_proxy.question)
                except:
                    pass

            user_answer.lab_proxy = lab_proxy
            user_answer.problem = problem
            user_answer.question = problem_proxy.question_text
            user_answer.quiz_id = problem_proxy.quiz_id
            user_answer.save()
