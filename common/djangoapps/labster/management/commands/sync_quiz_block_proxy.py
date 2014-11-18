from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from xmodule.modulestore.django import modulestore

from labster.models import LabProxy, QuizBlockProxy, QuizBlock, ProblemProxy, Problem
from labster.quiz_blocks import validate_lab_proxy


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.get(id=19)
        lab_proxies = LabProxy.objects.filter(is_active=True).order_by('id')
        for lab_proxy in lab_proxies:
            course, section, sub_section = validate_lab_proxy(lab_proxy)
            if not course:
                continue

            self.stdout.write("{}\n".format(lab_proxy.id))

            for unit in sub_section.get_children():
                try:
                    quiz_block = QuizBlock.objects.get(
                        lab=lab_proxy.lab,
                        element_id=unit.display_name,
                    )
                except QuizBlock.DoesNotExist:
                    modulestore().unpublish(unit.location, user.id)
                    continue

                try:
                    quiz_block_proxy = QuizBlockProxy.objects.get(
                        lab_proxy=lab_proxy, quiz_block=quiz_block)
                except QuizBlockProxy.DoesNotExist:
                    quiz_block_proxy = QuizBlockProxy(lab_proxy=lab_proxy, quiz_block=quiz_block)

                quiz_block_proxy.location = unit.location
                quiz_block_proxy.save()

                for component in unit.get_children():
                    try:
                        problem = Problem.objects.get(
                            quiz_block=quiz_block,
                            element_id=component.display_name)
                    except Problem.DoesNotExist:
                        modulestore().unpublish(component.location, user.id)
                        continue

                    try:
                        problem_proxy = ProblemProxy.objects.get(
                            quiz_block_proxy=quiz_block_proxy, problem=problem)
                    except ProblemProxy.DoesNotExist:
                        problem_proxy = ProblemProxy(
                            quiz_block_proxy=quiz_block_proxy, problem=problem)

                    problem_proxy.location = component.location
                    problem_proxy.save()

