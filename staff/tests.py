from django.test import TestCase
from django.urls import reverse
import json
from django.contrib.auth.models import User
from unittest import mock
from app.models import Feedback


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


class TestStaffFeedback(TestCase):

    def test_not_authenticated(self):
        """
        Not authenticated GET should redirect 302
        """
        response = self.client.get(reverse('staff_feedback_url'))
        self.assertEqual(response.status_code, 302)

    def test_normal_user(self):
        """
        Authenticated non-staff user GET should redirect 302
        """
        user = _create_normal_user()
        self.client.login(**user)
        response = self.client.get(reverse('staff_feedback_url'))
        self.assertEqual(response.status_code, 302)

    def test_success(self):
        """
        Authenticated staff GET should return 200 and some Feedback objects
        """
        obj1 = Feedback.objects.create(text='test1')
        obj2 = Feedback.objects.create(text='test2', email='example@gmail.com')
        user = _create_staff_user()
        self.client.login(**user)
        response = self.client.get(reverse('staff_feedback_url'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('objs', []).count(), 2)


class TestStaffFeedbackDelAll(TestCase):

    def test_ajax_get_request(self):
        """
        Ajax get-request should return status 400
        """
        response = self.client.get(reverse('staff_feedback_del_all'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)

    def test_non_authenticated(self):
        """
        Empty POST ajax should return status 400
        """
        response = self.client.post(reverse('staff_feedback_del_all'),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)

    def test_not_staff_user(self):
        """
        POST ajax from normal user should return status 400
        """
        user = _create_normal_user()
        self.client.login(**user)
        response = self.client.post(reverse('staff_feedback_del_all'),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)

    def test_success(self):
        """
        POST ajax from staff should delete all Feedback objects and return 200
        """
        obj1 = Feedback.objects.create(text='test1')
        obj2 = Feedback.objects.create(text='test2', email='example@gmail.com')
        self.assertEqual(Feedback.objects.all().count(), 2)
        user = _create_staff_user()
        self.client.login(**user)
        response = self.client.post(reverse('staff_feedback_del_all'),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Feedback.objects.all().count(), 0)


class TestStaffFeedbackDelSpec(TestCase):

    def test_ajax_get_request(self):
        """
        Ajax get-request should return status 400
        """
        response = self.client.get(reverse('staff_feedback_del_spec'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)

    def test_non_authenticated(self):
        """
        Empty POST ajax should return status 400
        """
        response = self.client.post(reverse('staff_feedback_del_spec'),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)

    def test_not_staff_user(self):
        """
        POST ajax from normal user should return status 400
        """
        user = _create_normal_user()
        self.client.login(**user)
        response = self.client.post(reverse('staff_feedback_del_spec'),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)

    def test_wrong_id(self):
        """
        Wrong id in POST ajax from staff should return 400
        """
        user = _create_staff_user()
        self.client.login(**user)
        response = self.client.post(reverse('staff_feedback_del_spec'),
                                    data={'obj_id': 123},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)

    def test_success(self):
        """
        Right id in POST ajax from staff should return 200 and delete specific Feedback
        """
        obj1 = Feedback.objects.create(text='test1')
        obj2 = Feedback.objects.create(text='test2', email='example@gmail.com')
        obj3 = Feedback.objects.create(text='test3', email='sas222@gmail.com')
        self.assertEqual(Feedback.objects.all().count(), 3)
        user = _create_staff_user()
        self.client.login(**user)
        response = self.client.post(reverse('staff_feedback_del_spec'),
                                    data={'obj_id': obj2.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Feedback.objects.all().count(), 2)
        self.assertEqual(Feedback.objects.all().first().text, 'test1')
        self.assertEqual(Feedback.objects.all().last().text, 'test3')
