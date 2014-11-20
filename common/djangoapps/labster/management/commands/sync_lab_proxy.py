from django.core.management.base import BaseCommand

from labster.models import LabProxy
from labster.proxies import sync_lab_proxy


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            lab_id = args[0]
        except:
            lab_id = None

        if lab_id:
            lab_proxies = LabProxy.objects.filter(is_active=True, id=lab_id)
        else:
            lab_proxies = LabProxy.objects.filter(is_active=True)

        total = lab_proxies.count()

        for index, lab_proxy in enumerate(lab_proxies, start=1):
            self.stdout.write("{}/{}\n".format(
                index, total))

            sync_lab_proxy(lab_proxy)
