from django.test import TestCase
from django.urls import reverse
import json
from unittest import mock
from .models import Feedback
import os
from django.conf import settings
import random
import string


class TestHandler404View(TestCase):

    def test_404(self):
        """
        Going to unknown page should return status 404 and custom error page
        """
        response = self.client.get('NOT_EXISTING_PAGE/123test123/')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Oops, Page Not Found!', response.content.decode('utf-8'))


class TestIndexPageView(TestCase):

    def test_get_request(self):
        """
        GET request should return main page in image_to_ascii mode
        """
        response = self.client.get(reverse('index_page_url'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('img2ascii chosen', response.content.decode('utf-8'))
        self.assertNotIn('txt2ascii chosen', response.content.decode('utf-8'))

    def test_post_request(self):
        """
        POST request should return main page in image_to_ascii mode
        """
        response = self.client.post(reverse('index_page_url'), data={'data': 'data'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('img2ascii chosen', response.content.decode('utf-8'))
        self.assertNotIn('txt2ascii chosen', response.content.decode('utf-8'))


class TestIndexTxtPageView(TestCase):

    def test_get_request(self):
        """
        GET request should return main page in text_to_ascii mode
        """
        response = self.client.get(reverse('index_txt_page_url'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('txt2ascii chosen', response.content.decode('utf-8'))
        self.assertNotIn('img2ascii chosen', response.content.decode('utf-8'))

    def test_post_request(self):
        """
        POST request should return main page in text_to_ascii mode
        """
        response = self.client.post(reverse('index_txt_page_url'), data={'data': 'data'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('txt2ascii chosen', response.content.decode('utf-8'))
        self.assertNotIn('img2ascii chosen', response.content.decode('utf-8'))


class TestAboutView(TestCase):

    def test_render(self):
        """
        GET and POST should return page 200
        """
        response = self.client.get(reverse('about_url'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('about_url'))
        self.assertEqual(response.status_code, 200)


class TestPolicyPrivacyView(TestCase):

    def test_render(self):
        """
        GET and POST should return page 200
        """
        response = self.client.get(reverse('policy_privacy_url'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('policy_privacy_url'))
        self.assertEqual(response.status_code, 200)


class TestPolicyCookieView(TestCase):

    def test_render(self):
        """
        GET and POST should return page 200
        """
        response = self.client.get(reverse('policy_cookie_url'))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('policy_cookie_url'))
        self.assertEqual(response.status_code, 200)


class TestFeedbackView(TestCase):

    def test_get_request(self):
        """
        GET request should return page 200 with form
        """
        response = self.client.get(reverse('feedback_url'))
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.context.get('form', None), None)

    def test_post_wrong_data(self):
        """
        POST with wrong data should return 200 and errors
        """
        data = {'text': 'a' * 600, 'email': 'email123'}  # a*600 is higher than limit 512 symbols
        response = self.client.post(reverse('feedback_url'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('class="error"', response.content.decode('utf-8'))
        self.assertEqual(Feedback.objects.all().count(), 0)

    def test_post_right_data_no_captcha(self):
        """
        POST with right data but without capthca completion should return 200 and errors
        """
        data = {'text': 'text123', 'email': 'example@gmail.com', 'agreement': 'True'}
        response = self.client.post(reverse('feedback_url'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('class="error"', response.content.decode('utf-8'))
        self.assertEqual(Feedback.objects.all().count(), 0)

    @mock.patch("captcha.fields.ReCaptchaField.validate")
    def test_wrong_text_limit(self, mock):
        """
        POST with captcha but wrong text limit should return 200 and error
        """
        data = {'text': 'a' * 600, 'email': 'example@gmail.com', 'agreement': 'True'}
        response = self.client.post(reverse('feedback_url'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('class="error"', response.content.decode('utf-8'))
        self.assertEqual(Feedback.objects.all().count(), 0)

    @mock.patch("captcha.fields.ReCaptchaField.validate")
    def test_wrong_email(self, mock):
        """
        POST with captcha but wrong email should return 200 and error
        """
        data = {'text': 'text123', 'email': 'emeil#gmeil,com', 'agreement': 'True'}
        response = self.client.post(reverse('feedback_url'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('class="error"', response.content.decode('utf-8'))
        self.assertEqual(Feedback.objects.all().count(), 0)

    @mock.patch("captcha.fields.ReCaptchaField.validate")
    def test_success(self, mock):
        """
        POST with right data and captcha should return 200 reload and create Feedback object
        """
        data = {'text': 'text123', 'email': 'example@gmail.com', 'agreement': 'True'}
        response = self.client.post(reverse('feedback_url'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('class="error"', response.content.decode('utf-8'))
        self.assertEqual(Feedback.objects.all()[0].text, 'text123')

    def test_ajax_get_request(self):
        """
        Ajax GET should return 405 method not allowed
        """
        response = self.client.get(reverse('feedback_url'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 405)

    def test_ajax_post_wrong_data(self):
        """
        POST with wrong data should return 400 and errors
        """
        data = {'text': 'a' * 600, 'email': 'email123'}  # a*600 is higher than limit 512 symbols
        response = self.client.post(reverse('feedback_url'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 400)
        self.assertNotEqual(json_content.get('errors', None), None)
        self.assertEqual(Feedback.objects.all().count(), 0)

    def test_ajax_post_right_data_no_captcha(self):
        """
        POST with right data but without capthca completion should return 400 and errors
        """
        data = {'text': 'text123', 'email': 'example@gmail.com', 'agreement': 'True'}
        response = self.client.post(reverse('feedback_url'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 400)
        self.assertNotEqual(json_content.get('errors', None), None)
        self.assertEqual(Feedback.objects.all().count(), 0)

    @mock.patch("captcha.fields.ReCaptchaField.validate")
    def test_ajax_wrong_text_limit(self, mock):
        """
        POST with captcha but wrong text limit should return 400 and error
        """
        data = {'text': 'a' * 600, 'email': 'example@gmail.com', 'agreement': 'True'}
        response = self.client.post(reverse('feedback_url'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 400)
        self.assertNotEqual(json_content.get('errors', None), None)
        self.assertEqual(Feedback.objects.all().count(), 0)

    @mock.patch("captcha.fields.ReCaptchaField.validate")
    def test_ajax_wrong_email(self, mock):
        """
        POST with captcha but wrong email should return 400 and error
        """
        data = {'text': 'text123', 'email': 'emeil#gmeil,com', 'agreement': 'True'}
        response = self.client.post(reverse('feedback_url'), data=data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 400)
        self.assertNotEqual(json_content.get('errors', None), None)
        self.assertEqual(Feedback.objects.all().count(), 0)

    @mock.patch("captcha.fields.ReCaptchaField.validate")
    def test_ajax_success(self, mock):
        """
        POST with right data and captcha should return 302 and create Feedback object
        """
        data = {'text': 'text123', 'email': 'example@gmail.com', 'agreement': 'True'}
        response = self.client.post(reverse('feedback_url'), data=data, follow=True,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_content.get('errors', None), None)
        self.assertEqual(Feedback.objects.all()[0].text, 'text123')


class TestImageToAsciiGeneratorView(TestCase):

    def _test_image(self, path):
        """
        Ajax POST with right image type should return 200, arts, and create temporary file
        """
        with open(path, mode='rb') as file:
            response = self.client.post(reverse('image_to_ascii_generator_url'),
                                        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                        data={'img': file},
                                        format='multipart')
        json_content = json.loads(response.content, encoding='utf-8')
        file_name = json_content.get('file_name', '')
        file_path = os.path.join(settings.BASE_DIR, '_temporary_images/', file_name)
        self.assertEqual(response.status_code, 200)
        # Check if there's 3 or more arts
        self.assertGreaterEqual(len(json_content.get('arts', [])), 3)
        # Check if image is actually saved
        self.assertTrue(os.path.exists(file_path))
        # Delete temporary image after test
        os.remove(file_path)

    def test_non_ajax(self):
        """
        All non-ajax requests should redirect to main page
        """
        response = self.client.get(reverse('image_to_ascii_generator_url'), follow=True)
        self.assertEqual(response.redirect_chain[0][0], '/')
        self.assertEqual(response.redirect_chain[0][1], 302)
        response = self.client.post(reverse('image_to_ascii_generator_url'), follow=True)
        self.assertEqual(response.redirect_chain[0][0], '/')
        self.assertEqual(response.redirect_chain[0][1], 302)

    def test_ajax_get(self):
        """
        Ajax GET should return 405 not allowed
        """
        response = self.client.get(reverse('image_to_ascii_generator_url'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 405)

    def test_ajax_post_no_data(self):
        """
        Ajax POST without any data (!img/!file_name, num_cols, brightness, contrast) should return 400
        """
        response = self.client.post(reverse('image_to_ascii_generator_url'),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={})
        self.assertEqual(response.status_code, 400)

    def test_ajax_post_wrong_filename(self):
        """
        Ajax POST with wrong file_name should return 400
        """
        response = self.client.post(reverse('image_to_ascii_generator_url'),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'file_name': 'test123ABCDEFG'})
        self.assertEqual(response.status_code, 400)

    def test_ajax_post_wrong_image(self):
        """
        Ajax POST with wrong file should return 400
        """
        with open('__test_images/test_img_bad.jpg', mode='rb') as file:
            response = self.client.post(reverse('image_to_ascii_generator_url'),
                                        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                        data={'img': file},
                                        format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_ajax_post_image_type_jpg(self):
        self._test_image('__test_images/w3c_home.jpg')
        self._test_image('__test_images/w3c_home.jpg')
        self._test_image('__test_images/w3c_home_256.jpg')
        self._test_image('__test_images/w3c_home_gray.jpg')
        self._test_image('__test_images/test_img_good.jpg')

    def test_ajax_post_image_type_png(self):
        self._test_image('__test_images/w3c_home.png')
        self._test_image('__test_images/w3c_home_2.png')
        self._test_image('__test_images/w3c_home_256.png')
        self._test_image('__test_images/w3c_home_gray.png')

    def test_ajax_post_image_type_ico(self):
        self._test_image('__test_images/ICO.ico')

    def test_ajax_post_image_type_webp(self):
        self._test_image('__test_images/WEBP.webp')

    def test_ajax_post_image_type_bmp(self):
        self._test_image('__test_images/w3c_home.bmp')
        self._test_image('__test_images/w3c_home_2.bmp')
        self._test_image('__test_images/w3c_home_256.bmp')
        self._test_image('__test_images/w3c_home_gray.bmp')

    def test_ajax_post_image_type_gif(self):
        self._test_image('__test_images/w3c_home.gif')
        self._test_image('__test_images/w3c_home_2.gif')
        self._test_image('__test_images/w3c_home_256.gif')
        self._test_image('__test_images/w3c_home_animation.gif')
        self._test_image('__test_images/w3c_home_gray.gif')

    def test_ajax_post_right_image_high_num_cols(self):
        """
        Ajax POST with right image but high amount of num_cols should return arts with num_cols=300
        """
        with open('__test_images/test_img_good.jpg', mode='rb') as file:
            response = self.client.post(reverse('image_to_ascii_generator_url'),
                                        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                        data={'img': file, 'num_cols': 100000},
                                        format='multipart')
        json_content = json.loads(response.content, encoding='utf-8')
        file_name = json_content.get('file_name', '')
        file_path = os.path.join(settings.BASE_DIR, '_temporary_images/', file_name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_content.get('num_cols', 0), 300)
        os.remove(file_path)

    def test_ajax_post_right_image_wrong_settings(self):
        """
        Ajax POST with right image but wrong settings input should return 200 with arts but with default settings
        """
        with open('__test_images/test_img_good.jpg', mode='rb') as file:
            response = self.client.post(reverse('image_to_ascii_generator_url'),
                                        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                        data={'img': file,
                                              'num_cols': 'HELLO WORLD!',
                                              'brightness': 'HELLO WORLD!',
                                              'contrast': 'HELLO WORLD!'},
                                        format='multipart')
        json_content = json.loads(response.content, encoding='utf-8')
        file_name = json_content.get('file_name', '')
        file_path = os.path.join(settings.BASE_DIR, '_temporary_images/', file_name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_content.get('num_cols', 0), 90)
        self.assertEqual(json_content.get('brightness', 0), 100)
        self.assertEqual(json_content.get('contrast', 0), 100)
        os.remove(file_path)

    def test_ajax_post_right_image_with_settings(self):
        """
        Ajax POST with right image and some settings, should return 200 and settings back with new arts
        """
        with open('__test_images/test_img_good.jpg', mode='rb') as file:
            response = self.client.post(reverse('image_to_ascii_generator_url'),
                                        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                        data={'img': file,
                                              'num_cols': 125,
                                              'brightness': 200,
                                              'contrast': 500},
                                        format='multipart')
        json_content = json.loads(response.content, encoding='utf-8')
        file_name = json_content.get('file_name', '')
        file_path = os.path.join(settings.BASE_DIR, '_temporary_images/', file_name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_content.get('num_cols', 0), 125)
        self.assertEqual(json_content.get('brightness', 0), 200)
        self.assertEqual(json_content.get('contrast', 0), 500)
        os.remove(file_path)

    def test_ajax_post_right_file_name(self):
        """
        Ajax POST with right file_name and settings should return new arts and settings without actual file upload
        """
        file_name = 'test_image_' + ''.join(random.choices(string.ascii_lowercase, k=10)) + '.jpg'
        file_path = os.path.join(settings.BASE_DIR, '_temporary_images/', file_name)
        with open('__test_images/test_img_good.jpg', mode='rb') as file:
            with open(file_path, 'wb') as file_new:
                file_new.write(file.read())
        response = self.client.post(reverse('image_to_ascii_generator_url'),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'file_name': file_name,
                                          'num_cols': 125,
                                          'brightness': 200,
                                          'contrast': 500},
                                    format='multipart')
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_content.get('file_name', ''), file_name)
        self.assertGreaterEqual(len(json_content.get('arts', [])), 3)
        self.assertEqual(json_content.get('num_cols', 0), 125)
        self.assertEqual(json_content.get('brightness', 0), 200)
        self.assertEqual(json_content.get('contrast', 0), 500)
        os.remove(file_path)


class TestTextToAsciiGeneratorView(TestCase):

    def test_non_ajax(self):
        """
        All non-ajax requests should redirect to main page (txt mode)
        """
        response = self.client.get(reverse('text_to_ascii_generator_url'), follow=True)
        self.assertEqual(response.redirect_chain[0][0], '/t/')
        self.assertEqual(response.redirect_chain[0][1], 302)
        response = self.client.post(reverse('text_to_ascii_generator_url'), follow=True)
        self.assertEqual(response.redirect_chain[0][0], '/t/')
        self.assertEqual(response.redirect_chain[0][1], 302)

    def test_ajax_get(self):
        """
        Ajax GET should return 405 not allowed
        """
        response = self.client.get(reverse('text_to_ascii_generator_url'),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 405)

    def test_ajax_post_no_data(self):
        """
        Ajax POST without any data should return 200 and arts with default text in single_line mode
        """
        response = self.client.post(reverse('text_to_ascii_generator_url'),
                                    data={},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(json_content.get('results', [])), 10)

    def test_ajax_post_line_modes(self):
        """
        Ajax POST requests with different line modes should return different amount of arts
        """
        response1 = self.client.post(reverse('text_to_ascii_generator_url'),
                                     data={'txt': 'test text'},
                                     HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        response2 = self.client.post(reverse('text_to_ascii_generator_url'),
                                     data={'txt_multi': 'test\ntext\n123',
                                           'multiple_strings': 'True'},
                                     HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_content1 = json.loads(response1.content, encoding='utf-8')
        json_content2 = json.loads(response2.content, encoding='utf-8')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertNotEqual(len(json_content1.get('results', [])), len(json_content2.get('results', [])))

    def test_ajax_post_wrong_text_input(self):
        """
        Ajax POST with cursed input text should return 400
        """
        response = self.client.post(reverse('text_to_ascii_generator_url'),
                                    data={'txt': '򣠦ඪ󧯁ⶵӡ؎ᱜ'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
