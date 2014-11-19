from django.core.management.base import BaseCommand

from labster.models import Problem
from labster_adaptive.models import Problem as AdaptiveProblem


class Command(BaseCommand):

    def handle(self, *args, **options):
        adaptive_problems = AdaptiveProblem.objects.all()
        for ap in adaptive_problems:
            problem = Problem.objects.get(element_id=ap.item_number)
            problem.answer_type = ap.answer_type
            problem.number_of_destractors = ap.number_of_destractors
            problem.discrimination = ap.discrimination
            problem.guessing = ap.guessing
            problem.image_url = ap.image_url
            problem.save()
