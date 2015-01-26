from django.core.management.base import BaseCommand

from django.contrib.auth.models import User


# edx+test0001@labster.com
EMAIL_FORMAT = "edx+test{number}@labster.com"
USERNAME_FORMAT = "edx_test{number}"


def get_password(email):
    return email.split('@')[0]


class Command(BaseCommand):

    def handle(self, *args, **options):
        number = args[0]
        try:
            start = args[1]
        except:
            start = 0

        finished = False
        total = 0
        current = start

        while not finished:
            username = USERNAME_FORMAT.format(number=str(current).zfill(4))
            email = EMAIL_FORMAT.format(number=str(current).zfill(4))
            password = get_password(email)

            try:
                User.objects.get(email=email)
            except User.DoesNotExist:
                User.objects.get_or_create(
                    username=username,
                    email=email,
                    password=password)
                total += 1

                self.stdout.write("{} -> email: {}, password: {}\n".format(
                    total, email, password))

            current += 1

            if int(total) == int(number):
                finished = True
