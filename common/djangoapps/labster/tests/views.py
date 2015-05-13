from django.core.urlresolvers import reverse


class ViewTestMixin(object):

    @property
    def login_url(self):
        return "{}?next={}".format(reverse('login'), self.url)

    def test_get_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)

    def test_get_logged_in_not_staff(self):
        self.client.login(username='username', password='password')

        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)


class StaffViewTestMixin(ViewTestMixin):

    def test_get_logged_in_not_staff(self):
        self.user.is_staff = False
        self.user.save()
        self.client.login(username='username', password='password')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_get_logged_in_staff(self):
        self.client.login(username='username', password='password')

        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
