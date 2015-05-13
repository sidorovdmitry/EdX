from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase

from labster.models import LabsterUser
from labster.users.forms import LabsterUserForm
from student.models import UserProfile


class LabsterUserFormTest(TestCase):

    def setUp(self):
        self.data = {
            'name': "First Last",
            'email': "new@user.com",
            'user_is_active': "1",
            'password': "password",
            'gender': "m",
            'is_active': "1",
            'level_of_education': "hs",
            'user_type': "2",
            'user_school_level': "5",
            'phone_number': "12345",
            'organization_name': "The Cool People",
            'nationality': "ID",
            'unique_id': "123123",
            'language': "en",
            'date_of_birth': str(date.today()),
        }

    def test_initial(self):
        user = User.objects.create_user('UserName', 'user@name.com', 'password')
        user_profile, _ = UserProfile.objects.get_or_create(user=user)
        user_profile.name = "User Name"
        user_profile.gender = "m"
        user_profile.level_of_education = "hs"
        user_profile.save()

        labster_user = LabsterUser.objects.get(user=user)
        labster_user.is_active = True
        labster_user.user_type = 2
        labster_user.user_school_level = 5
        labster_user.phone_number = "12345"
        labster_user.organization_name = "The Cool People"
        labster_user.nationality = "ID"
        labster_user.language = "en"
        labster_user.unique_id = "123123"
        labster_user.date_of_birth = date.today()
        labster_user.save()

        form = LabsterUserForm(instance=labster_user)
        self.assertEqual(form.fields['user_is_active'].initial, user.is_active)
        self.assertEqual(form.fields['email'].initial, user.email)

        self.assertEqual(form.fields['name'].initial, user_profile.name)
        self.assertEqual(form.fields['gender'].initial, user_profile.gender)
        self.assertEqual(form.fields['level_of_education'].initial, user_profile.level_of_education)

        self.assertEqual(form.fields['is_active'].initial, labster_user.is_active)
        self.assertEqual(form.fields['user_type'].initial, labster_user.user_type)
        self.assertEqual(form.fields['user_school_level'].initial, labster_user.user_school_level)
        self.assertEqual(form.fields['phone_number'].initial, labster_user.phone_number)
        self.assertEqual(form.fields['organization_name'].initial, labster_user.organization_name)
        self.assertEqual(form.fields['nationality'].initial, labster_user.nationality)
        self.assertEqual(form.fields['unique_id'].initial, labster_user.unique_id)
        self.assertEqual(form.fields['language'].initial, labster_user.language)
        self.assertEqual(form.fields['date_of_birth'].initial, labster_user.date_of_birth)

    def test_create_valid(self):
        data = {
            'name': "First Last",
            'email': "new@user.com",
            'password': "password",
        }

        form = LabsterUserForm(data)
        self.assertTrue(form.is_valid())

    def test_create_email_is_used(self):
        User.objects.create_user('new@user.com', 'new@user.com', 'user')

        data = {
            'name': "First Last",
            'email': "new@user.com",
        }

        form = LabsterUserForm(data)
        self.assertFalse(form.is_valid())

    def test_create_save(self):
        data = self.data.copy()

        form = LabsterUserForm(data)
        form.is_valid()
        labster_user = form.save()

        user = User.objects.get(id=labster_user.user.id)
        user_profile = UserProfile.objects.get(user=user)
        labster_user = LabsterUser.objects.get(user=user)

        self.assertEqual(user.email, data['email'])
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password(data['password']))

        self.assertEqual(user_profile.name, data['name'])
        self.assertEqual(user_profile.gender, data['gender'])
        self.assertEqual(user_profile.level_of_education, data['level_of_education'])

        self.assertTrue(labster_user.is_active)
        self.assertEqual(labster_user.user_type, int(data['user_type']))
        self.assertEqual(labster_user.user_school_level, int(data['user_school_level']))
        self.assertEqual(labster_user.phone_number, data['phone_number'])
        self.assertEqual(labster_user.organization_name, data['organization_name'])
        self.assertEqual(labster_user.nationality, data['nationality'])
        self.assertEqual(labster_user.unique_id, data['unique_id'])
        self.assertEqual(labster_user.language, data['language'])
        self.assertEqual(str(labster_user.date_of_birth), data['date_of_birth'])

    def test_update_valid(self):
        user = User.objects.create_user('new@user.com', 'new@user.com', 'user')
        UserProfile.objects.get_or_create(user=user)
        labster_user = user.labster_user

        data = {
            'name': "First Last",
            'email': "other@user.com",
        }

        form = LabsterUserForm(data, instance=labster_user)
        self.assertTrue(form.is_valid())

    def test_update_save(self):
        user = User.objects.create_user('new@user.com', 'new@user.com', 'user')
        user.is_active = False
        user.save()

        UserProfile.objects.get_or_create(user=user)
        old_user_id = user.id

        labster_user = user.labster_user
        labster_user.is_active = False
        labster_user.save()

        data = self.data.copy()

        form = LabsterUserForm(data, instance=labster_user)
        form.is_valid()
        labster_user = form.save()

        user = User.objects.get(id=labster_user.user.id)
        user_profile = UserProfile.objects.get(user=user)
        labster_user = LabsterUser.objects.get(user=user)

        self.assertEqual(user.id, old_user_id)

        self.assertEqual(user.email, data['email'])
        self.assertTrue(user.is_active)
        self.assertFalse(user.check_password(data['password']))
        self.assertTrue(user.check_password('user'))

        self.assertEqual(user_profile.name, data['name'])
        self.assertEqual(user_profile.gender, data['gender'])
        self.assertEqual(user_profile.level_of_education, data['level_of_education'])

        self.assertTrue(labster_user.is_active)
        self.assertEqual(labster_user.user_type, int(data['user_type']))
        self.assertEqual(labster_user.user_school_level, int(data['user_school_level']))
        self.assertEqual(labster_user.phone_number, data['phone_number'])
        self.assertEqual(labster_user.organization_name, data['organization_name'])
        self.assertEqual(labster_user.nationality, data['nationality'])
        self.assertEqual(labster_user.unique_id, data['unique_id'])
        self.assertEqual(labster_user.language, data['language'])
        self.assertEqual(str(labster_user.date_of_birth), data['date_of_birth'])

    def test_update_email_is_used(self):
        User.objects.create_user('other@user.com', 'other@user.com', 'user')
        user = User.objects.create_user('new@user.com', 'new@user.com', 'user')
        UserProfile.objects.get_or_create(user=user)
        labster_user = user.labster_user

        data = {
            'name': "First Last",
            'email': "other@user.com",
        }

        form = LabsterUserForm(data, instance=labster_user)
        self.assertFalse(form.is_valid())

    def test_update_inactive(self):
        user = User.objects.create_user('new@user.com', 'new@user.com', 'user')
        UserProfile.objects.get_or_create(user=user)
        labster_user = LabsterUser.objects.get(user=user)

        data = {
            'name': "First Last",
            'email': "new@user.com",
        }

        form = LabsterUserForm(data, instance=labster_user)
        form.is_valid()
        labster_user = form.save()
        user = User.objects.get(id=labster_user.user.id)

        self.assertFalse(user.is_active)

    def test_update_no_password(self):
        user = User.objects.create_user('new@user.com', 'new@user.com', 'user')
        UserProfile.objects.get_or_create(user=user)
        labster_user = user.labster_user

        data = {
            'name': "First Last",
            'email': "new@user.com",
        }

        form = LabsterUserForm(data, instance=labster_user)
        form.is_valid()
        labster_user = form.save()
        user = User.objects.get(id=labster_user.user.id)

        self.assertTrue(user.check_password('user'))
