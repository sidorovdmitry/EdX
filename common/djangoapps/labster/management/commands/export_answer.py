import csv

from django.core.management.base import BaseCommand, CommandError

from labster.models import LabProxy, Problem, QuizBlock, UserAnswer
from labster.proxies import generate_lab_proxy_data


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            lab_id = args[0]
        except:
            raise CommandError("Missing lab proxy's id arg")

        try:
            lab_proxy = LabProxy.objects.get(id=lab_id)
        except LabProxy.DoesNotExist:
            raise CommandError("Missing lab proxy")

        generate_lab_proxy_data(lab_proxy)
