from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest import mock


def _create_staff_user(username='admin', password='admin'):
    user = User.objects.create_user(username=username, password=password)
    user.is_staff = True
    user.save()
    return {'username': username, 'password': password}


def _create_normal_user(username='user', password='user'):
    user = User.objects.create_user(username=username, password=password)
    return {'username': username, 'password': password}


class TestStaffAuthenticationView(TestCase):

    def test_authenticated_requests(self):
        """
        GET and POST authenticated requests should return 302 redirect to main page
        """
        user = _create_normal_user()
        self.client.login(**user)
        response = self.client.get(reverse('staff_authentication_url'), follow=True)
        self.assertRedirects(response, '/', status_code=302)
        response = self.client.post(reverse('staff_authentication_url'), follow=True)
        self.assertRedirects(response, '/', status_code=302)

    def test_not_authenticated_requests(self):
        """
        GET and POST not-authenticated requests should return 200
        """
        response = self.client.get(reverse('staff_authentication_url'), follow=True)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('staff_authentication_url'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_post_wrong_data(self):
        """
        Wrong post_data should return errors and status 200
        """
        data = {
            'username': 'user123',
            'password': 'pass123'
        }
        response = self.client.post(reverse('staff_authentication_url'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('class="error"', response.content.decode('utf-8'))

    @mock.patch("captcha.fields.ReCaptchaField.validate")
    def test_post_normal_user_login(self, mock):
        """
        Can't login into non-staff account, should return errors and status 200
        """

        user = _create_normal_user()
        response = self.client.post(reverse('staff_authentication_url'), data=user, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('class="error"', response.content.decode('utf-8'))

    @mock.patch("captcha.fields.ReCaptchaField.validate")
    def test_post_wrong_username(self, mock):
        """
        Wrong username register should return errors and status 200
        """
        user = _create_staff_user('admin', 'admin')
        user['username'] = 'adMin'
        response = self.client.post(reverse('staff_authentication_url'), data=user, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('class="error"', response.content.decode('utf-8'))

    @mock.patch("captcha.fields.ReCaptchaField.validate")
    def test_post_wrong_password(self, mock):
        """
        Wrong password register should return errors and status 200
        """
        user = _create_staff_user('admin', 'admin')
        user['password'] = 'adMin'
        response = self.client.post(reverse('staff_authentication_url'), data=user, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('class="error"', response.content.decode('utf-8'))

    def test_no_capthca_right_data(self):
        """
        Right username and password but without captcha should return errors and status 200
        """
        user = _create_staff_user('admin', 'admin')
        response = self.client.post(reverse('staff_authentication_url'), data=user, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('class="error"', response.content.decode('utf-8'))

    @mock.patch("captcha.fields.ReCaptchaField.validate")
    def test_success(self, mock):
        """
        Right data and validated captcha should redirect to main page after authentication
        """
        user = _create_staff_user('admin', 'admin')
        response = self.client.post(reverse('staff_authentication_url'), data=user, follow=True)
        self.assertRedirects(response, '/', status_code=302)
        self.assertNotIn('class="error"', response.content.decode('utf-8'))


class TestStaffLogout(TestCase):

    def test_staff_logged_out(self):
        """
        If staff was logged, he should not more see special links, also redirect 302 to main page
        """
        user = _create_staff_user('admin', 'admin')
        self.client.login(**user)
        response = self.client.get(reverse('index_page_url'))
        self.assertIn('$Logout', response.content.decode('utf-8'))
        response = self.client.get(reverse('staff_logout_url'))
        self.assertRedirects(response, '/', status_code=302)
        self.assertNotIn('$Logout', response.content.decode('utf-8'))
