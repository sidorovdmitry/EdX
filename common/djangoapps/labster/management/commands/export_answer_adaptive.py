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
            year, month, day = args[1].split('-')
        except:
            year = 2014
            month = 12
            day = None

        try:
            lab_proxy = LabProxy.objects.get(id=lab_id)
        except LabProxy.DoesNotExist:
            raise CommandError("Missing lab proxy")

        filters = {}

        if year:
            filters['created_at__year'] = year
        if month:
            filters['created_at__month'] = month
        if day:
            filters['created_at__day'] = day

        quiz_blocks = ['QuizblockPreTest', 'QuizblockPostTest']
        file_name = "adaptive_prepost_{}{}{}.csv".format(year, month, day)
        generate_lab_proxy_data(lab_proxy, quiz_blocks=quiz_blocks, filters=filters,
                                file_name=file_name)

        quiz_ids = ["Cyto-{}-Post".format(i) for i in range(11, 41)]
        file_name = "adaptive_answers_{}{}{}.csv".format(year, month, day)
        score_file_name = "adaptive_scores_{}{}{}.csv".format(year, month, day)
        generate_lab_proxy_data(lab_proxy, quiz_ids=quiz_ids, filters=filters,
                                file_name=file_name, process_score=True,
                                score_file_name=score_file_name, active_only=True)
