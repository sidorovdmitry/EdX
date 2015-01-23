import csv

from django.core.management.base import BaseCommand

from labster_search.models import LabKeyword
from labster.models import Lab


class Command(BaseCommand):

    def handle(self, *args, **options):
        file_name = 'data/primary_keys.csv'

        with open(file_name, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                lab_name, keyword, rank = row
                rank = int(float(rank) * 100)

                lab = Lab.objects.get(name=lab_name)
                obj, _ = LabKeyword.objects.get_or_create(
                    lab=lab,
                    keyword=keyword.lower(),
                    keyword_type=LabKeyword.KEYWORD_PRIMARY,
                )

                obj.source = LabKeyword.SOURCE_MANUAL
                obj.rank = rank
                obj.save()
