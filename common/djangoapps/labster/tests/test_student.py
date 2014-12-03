import unittest

from django.contrib.auth.models import User
from labster.student import generate_username, generate_unique_username


class GenerateUsernameTest(unittest.TestCase):

    def test_all_word_no_index(self):
        name = "Aldiantoro Nugroho"
        username = "AldiantoroNugroho"

        self.assertEqual(generate_username(name, 0), username)

    def test_with_number(self):
        name = "Aldiantoro Nugroho 123"
        username = "AldiantoroNugroho123"

    def test_with_other_chars(self):
        name = "Aldiantoro #@%@% Nugroho"
        username = "AldiantoroNugroho"

        self.assertEqual(generate_username(name, 0), username)

    def test_with_index_larger_than_zero(self):
        name = "Aldiantoro Nugroho"
        username = "AldiantoroNugroho1"

        self.assertEqual(generate_username(name, 1), username)


class GenerateUniqueUsername(unittest.TestCase):

    def test_not_used(self):
        name = "Aldiantoro Nugroho"
        username = "AldiantoroNugroho"

        self.assertEqual(generate_unique_username(name, User), username)

    def test_used_different_case(self):
        name = "Aldiantoro Nugroho"
        username = "AldiantoroNugroho"

        User.objects.create_user(username.upper(), 'aldi@email.com', 'password')

        username = "AldiantoroNugroho1"
        self.assertEqual(generate_unique_username(name, User), username)

    def test_used_by_one(self):
        name = "Bldiantoro Nugroho"
        username = "BldiantoroNugroho"

        User.objects.create_user(username, 'aldi@email.com', 'password')

        username = "BldiantoroNugroho1"
        self.assertEqual(generate_unique_username(name, User), username)

    def test_used_by_two(self):
        name = "Cldiantoro Nugroho"

        username = "CldiantoroNugroho"
        User.objects.create_user(username, 'aldi@email.com', 'password')

        username = "CldiantoroNugroho1"
        User.objects.create_user(username, 'aldi@email.com', 'password')

        username = "CldiantoroNugroho2"
        self.assertEqual(generate_unique_username(name, User), username)
