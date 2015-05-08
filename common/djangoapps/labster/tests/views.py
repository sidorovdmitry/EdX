from django.core.urlresolvers import reverse


class ViewTestMixin(object):

    @property
    def login_url(self):
        return "{}?next={}".format(reverse('account:login'), self.url)

    def test_get_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)

    def test_get_logged_in(self):
        self.client.login(username='username', password='password')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
