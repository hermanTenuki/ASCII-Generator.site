from django.test import TestCase
from django.urls import reverse
import json
from unittest import mock
from .models import *
import os
from django.conf import settings
import random
import string
from django.core.files import File


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


class TestSitemapXmlView(TestCase):

    def test_render(self):
        """
        GET and POST should return sitemap.xml and status 200
        """
        response = self.client.get(reverse('sitemap_xml'))
        content = response.content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(content), bytes)
        self.assertIn(bytes('xml', encoding='UTF-8'), content)
        response = self.client.post(reverse('sitemap_xml'))
        content = response.content
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(content), bytes)
        self.assertIn(bytes('xml', encoding='UTF-8'), content)


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
        data = {'text': 'a' * 1200, 'email': 'email123'}  # a*1200 is higher than limit 1024 symbols
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
        data = {'text': 'a' * 1200, 'email': 'example@gmail.com', 'agreement': 'True'}
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
        data = {'text': 'a' * 1200, 'email': 'email123'}  # a*1200 is higher than limit 1024 symbols
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
        data = {'text': 'a' * 1200, 'email': 'example@gmail.com', 'agreement': 'True'}
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
        file_path = os.path.join(settings.TEMPORARY_IMAGES, file_name)
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
        with open('_images/test/test_img_bad.jpg', mode='rb') as file:
            response = self.client.post(reverse('image_to_ascii_generator_url'),
                                        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                        data={'img': file},
                                        format='multipart')
        self.assertEqual(response.status_code, 400)

    def test_ajax_post_image_type_jpg(self):
        self._test_image('_images/test/w3c_home.jpg')
        self._test_image('_images/test/w3c_home.jpg')
        self._test_image('_images/test/w3c_home_256.jpg')
        self._test_image('_images/test/w3c_home_gray.jpg')
        self._test_image('_images/test/test_img_good.jpg')

    def test_ajax_post_image_type_png(self):
        self._test_image('_images/test/w3c_home.png')
        self._test_image('_images/test/w3c_home_2.png')
        self._test_image('_images/test/w3c_home_256.png')
        self._test_image('_images/test/w3c_home_gray.png')

    def test_ajax_post_image_type_ico(self):
        self._test_image('_images/test/ICO.ico')

    def test_ajax_post_image_type_webp(self):
        self._test_image('_images/test/WEBP.webp')

    def test_ajax_post_image_type_bmp(self):
        self._test_image('_images/test/w3c_home.bmp')
        self._test_image('_images/test/w3c_home_2.bmp')
        self._test_image('_images/test/w3c_home_256.bmp')
        self._test_image('_images/test/w3c_home_gray.bmp')

    def test_ajax_post_image_type_gif(self):
        self._test_image('_images/test/w3c_home.gif')
        self._test_image('_images/test/w3c_home_2.gif')
        self._test_image('_images/test/w3c_home_256.gif')
        self._test_image('_images/test/w3c_home_animation.gif')
        self._test_image('_images/test/w3c_home_gray.gif')

    def test_ajax_post_small_image_high_num_cols(self):
        """
        Ajax POST with small image but high amount of num_cols should return arts with adapted num_cols
        """
        with open('_images/test/test_img_good.jpg', mode='rb') as file:
            response = self.client.post(reverse('image_to_ascii_generator_url'),
                                        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                        data={'img': file, 'num_cols': 300},
                                        format='multipart')
        json_content = json.loads(response.content, encoding='utf-8')
        file_name = json_content.get('file_name', '')
        file_path = os.path.join(settings.TEMPORARY_IMAGES, file_name)
        self.assertEqual(response.status_code, 200)
        self.assertLess(json_content.get('num_cols', 0), 300)
        os.remove(file_path)

    def test_ajax_post_right_image_high_num_cols(self):
        """
        Ajax POST with right image but high amount of num_cols should return arts with num_cols=300
        """
        with open('_images/test/test_img_good_big.jpg', mode='rb') as file:
            response = self.client.post(reverse('image_to_ascii_generator_url'),
                                        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                        data={'img': file, 'num_cols': 100000},
                                        format='multipart')
        json_content = json.loads(response.content, encoding='utf-8')
        file_name = json_content.get('file_name', '')
        file_path = os.path.join(settings.TEMPORARY_IMAGES, file_name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_content.get('num_cols', 0), 300)
        os.remove(file_path)

    def test_ajax_post_right_image_wrong_settings(self):
        """
        Ajax POST with right image but wrong settings input should return 200 with arts but with default settings
        """
        with open('_images/test/test_img_good.jpg', mode='rb') as file:
            response = self.client.post(reverse('image_to_ascii_generator_url'),
                                        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                        data={'img': file,
                                              'num_cols': 'HELLO WORLD!',
                                              'brightness': 'HELLO WORLD!',
                                              'contrast': 'HELLO WORLD!'},
                                        format='multipart')
        json_content = json.loads(response.content, encoding='utf-8')
        file_name = json_content.get('file_name', '')
        file_path = os.path.join(settings.TEMPORARY_IMAGES, file_name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_content.get('num_cols', 0), 90)
        self.assertEqual(json_content.get('brightness', 0), 100)
        self.assertEqual(json_content.get('contrast', 0), 100)
        os.remove(file_path)

    def test_ajax_post_right_image_with_settings(self):
        """
        Ajax POST with right image and some settings, should return 200 and settings back with new arts
        """
        with open('_images/test/test_img_good.jpg', mode='rb') as file:
            response = self.client.post(reverse('image_to_ascii_generator_url'),
                                        HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                        data={'img': file,
                                              'num_cols': 125,
                                              'brightness': 200,
                                              'contrast': 500},
                                        format='multipart')
        json_content = json.loads(response.content, encoding='utf-8')
        file_name = json_content.get('file_name', '')
        file_path = os.path.join(settings.TEMPORARY_IMAGES, file_name)
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
        file_path = os.path.join(settings.TEMPORARY_IMAGES, file_name)
        with open('_images/test/test_img_good.jpg', mode='rb') as file:
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


class TestAsciiDetailView(TestCase):
    def test_wrong_ascii_url_code(self):
        """
        POST request with un-existing ascii_url_code should return 404
        """
        response = self.client.get(reverse('ascii_detail_url', kwargs={'ascii_url_code': '12345'}))
        self.assertEqual(response.status_code, 404)

    def test_success(self):
        """
        POST request right ascii_url_code should return 200
        """
        obj = GeneratedASCII.objects.create(preferred_output_method='testing123')
        response = self.client.get(reverse('ascii_detail_url', kwargs={'ascii_url_code': obj.url_code}))
        self.assertEqual(response.status_code, 200)
        obj.delete()

    def test_success_image_to_ascii_type(self):
        """
        POST request with right ascii_url_code and ImageToASCIIType should return 200 in Image to ASCII mode
        """
        obj = GeneratedASCII.objects.create(preferred_output_method='testing123')
        file = open('_images/test/test_img_good.jpg', mode='rb')
        obj_type = ImageToASCIIType.objects.create(generated_ascii=obj)
        obj_type.input_image.save(
            'test.jpg',
            File(file),
        )
        obj_type.save()
        file.close()
        response = self.client.get(reverse('ascii_detail_url', kwargs={'ascii_url_code': obj.url_code}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('img2ascii chosen', response.content.decode('utf-8'))
        self.assertNotIn('txt2ascii chosen', response.content.decode('utf-8'))
        os.remove('media/input_images/test.jpg')
        obj.delete()

    def test_success_text_to_ascii_type_single_line(self):
        """
        POST request with right ascii_url_code and ImageToASCIIType should return 200 in Text to ASCII mode,
        also in single line mode
        """
        obj = GeneratedASCII.objects.create(preferred_output_method='testing123')
        file = open('_images/test/test_img_good.jpg', mode='rb')
        obj_type = TextToASCIIType.objects.create(generated_ascii=obj,
                                                  input_text='testing')
        file.close()
        response = self.client.get(reverse('ascii_detail_url', kwargs={'ascii_url_code': obj.url_code}))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('img2ascii chosen', response.content.decode('utf-8'))
        self.assertIn('txt2ascii chosen', response.content.decode('utf-8'))
        self.assertNotIn('checked', response.content.decode('utf-8'))
        obj.delete()

    def test_success_text_to_ascii_type_multi_line(self):
        """
        POST request with right ascii_url_code and ImageToASCIIType should return 200 in Text to ASCII mode,
        also in single line mode
        """
        obj = GeneratedASCII.objects.create(preferred_output_method='testing123')
        file = open('_images/test/test_img_good.jpg', mode='rb')
        obj_type = TextToASCIIType.objects.create(generated_ascii=obj,
                                                  input_text='testing\ntext',
                                                  multi_line_mode=True)
        file.close()
        response = self.client.get(reverse('ascii_detail_url', kwargs={'ascii_url_code': obj.url_code}))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('img2ascii chosen', response.content.decode('utf-8'))
        self.assertIn('txt2ascii chosen', response.content.decode('utf-8'))
        self.assertIn('checked', response.content.decode('utf-8'))
        obj.delete()


class TestAsciiShareView(TestCase):
    def test_non_ajax_requests(self):
        """
        Non-ajax requests should return redirect 302
        """
        response = self.client.get(reverse('ascii_share_url'))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('ascii_share_url'))
        self.assertEqual(response.status_code, 302)

    def test_ajax_get_request(self):
        """
        Ajax GET should return 405 method not allowed
        """
        response = self.client.get(reverse('ascii_share_url'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 405)

    def test_ajax_post_no_data(self):
        """
        Ajax POST without any data should return 400
        """
        response = self.client.post(reverse('ascii_share_url'), HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={})
        self.assertEqual(response.status_code, 400)

    def test_ajax_blank_singleline_text(self):
        """
        Ajax POST to share blank single-line text should return 200 and create new objects in database
        """
        response = self.client.post(reverse('ascii_share_url'), HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'preferred_output_method': 'alpha'})
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 200)
        obj = GeneratedASCII.objects.first()
        self.assertEqual(obj.preferred_output_method, 'alpha')
        self.assertFalse(obj.is_hidden)
        self.assertEqual(obj.text_to_ascii_type.input_text, '')
        self.assertFalse(obj.text_to_ascii_type.multi_line_mode)
        self.assertIsNotNone(json_content.get('shared_redirect_url', None))
        OutputASCII.objects.get(generated_ascii=obj, method_name='alpha')
        obj.delete()

    def test_ajax_blank_multiline_text(self):
        """
        Ajax POST to share blank multi-line text should return 200 and create new objects in database
        """
        response = self.client.post(reverse('ascii_share_url'), HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'preferred_output_method': 'alpha',
                                          'multiple_strings': True})
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 200)
        obj = GeneratedASCII.objects.first()
        self.assertEqual(obj.preferred_output_method, 'alpha')
        self.assertFalse(obj.is_hidden)
        self.assertEqual(obj.text_to_ascii_type.input_text, '')
        self.assertTrue(obj.text_to_ascii_type.multi_line_mode)
        self.assertIsNotNone(json_content.get('shared_redirect_url', None))
        OutputASCII.objects.get(generated_ascii=obj, method_name='alpha')
        obj.delete()

    def test_ajax_singleline_text(self):
        """
        Ajax POST to share single-line text should return 200 and create new objects in database
        """
        response = self.client.post(reverse('ascii_share_url'), HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'preferred_output_method': 'alpha',
                                          'txt': 'single line text',
                                          'txt_multi': 'multi line\ntext'})
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 200)
        obj = GeneratedASCII.objects.first()
        self.assertEqual(obj.preferred_output_method, 'alpha')
        self.assertFalse(obj.is_hidden)
        self.assertEqual(obj.text_to_ascii_type.input_text, 'single line text')
        self.assertFalse(obj.text_to_ascii_type.multi_line_mode)
        self.assertIsNotNone(json_content.get('shared_redirect_url', None))
        OutputASCII.objects.get(generated_ascii=obj, method_name='alpha')
        obj.delete()

    def test_ajax_multiline_text(self):
        """
        Ajax POST to share multi-line text should return 200 and create new objects in database
        """
        response = self.client.post(reverse('ascii_share_url'), HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'preferred_output_method': 'alpha',
                                          'txt': 'single line text',
                                          'txt_multi': 'multi line\ntext',
                                          'multiple_strings': True})
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 200)
        obj = GeneratedASCII.objects.first()
        self.assertEqual(obj.preferred_output_method, 'alpha')
        self.assertFalse(obj.is_hidden)
        self.assertEqual(obj.text_to_ascii_type.input_text, 'multi line\ntext')
        self.assertTrue(obj.text_to_ascii_type.multi_line_mode)
        self.assertIsNotNone(json_content.get('shared_redirect_url', None))
        OutputASCII.objects.get(generated_ascii=obj, method_name='alpha')
        obj.delete()

    def test_ajax_image_wrong_file_name(self):
        """
        Ajax POST with wrong file_name should return 400
        """
        response = self.client.post(reverse('ascii_share_url'), HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'preferred_output_method': '1',
                                          'file_name': 'wrong file name.txt'})
        self.assertEqual(response.status_code, 400)

    def test_ajax_image_success(self):
        """
        Ajax POST with right file_name should return 200 and create new objects in database
        """
        file = open('_images/test/test_img_good.jpg', mode='rb')
        with open('_images/temporary/test_img_good.jpg', mode='wb') as file_new:
            file_new.write(file.read())
        file.close()
        response = self.client.post(reverse('ascii_share_url'), HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'preferred_output_method': '1',
                                          'file_name': 'test_img_good.jpg'})
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 200)
        obj = GeneratedASCII.objects.first()
        self.assertEqual(obj.preferred_output_method, '1')
        self.assertFalse(obj.is_hidden)
        self.assertIsNotNone(json_content.get('shared_redirect_url', None))
        image_to_ascii_type = ImageToASCIIType.objects.get(generated_ascii=obj)
        image_to_ascii_options = ImageToASCIIOptions.objects.get(image_to_ascii_type=image_to_ascii_type)
        OutputASCII.objects.get(generated_ascii=obj, method_name='1')
        self.assertEqual(image_to_ascii_options.columns, '90')
        self.assertEqual(image_to_ascii_options.brightness, '100')
        self.assertEqual(image_to_ascii_options.contrast, '100')
        os.remove(image_to_ascii_type.input_image.path)
        obj.delete()

    def test_ajax_only_image(self):
        """
        Ajax POST with right file_name but without preferred_output_image should return 400
        """
        file = open('_images/test/test_img_good.jpg', mode='rb')
        with open('_images/temporary/test_img_good.jpg', mode='wb') as file_new:
            file_new.write(file.read())
        file.close()
        response = self.client.post(reverse('ascii_share_url'), HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'file_name': 'test_img_good.jpg'})
        self.assertEqual(response.status_code, 400)

    def test_ajax_image_success_with_settings(self):
        """
        Ajax POST with right file_name and custom settings should return 200 and create new objects in database
        """
        file = open('_images/test/test_img_good.jpg', mode='rb')
        with open('_images/temporary/test_img_good.jpg', mode='wb') as file_new:
            file_new.write(file.read())
        file.close()
        response = self.client.post(reverse('ascii_share_url'), HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'preferred_output_method': '1',
                                          'file_name': 'test_img_good.jpg',
                                          'num_cols': 150,
                                          'brightness': 50,
                                          'contrast': 123})
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 200)
        obj = GeneratedASCII.objects.first()
        self.assertEqual(obj.preferred_output_method, '1')
        self.assertFalse(obj.is_hidden)
        self.assertIsNotNone(json_content.get('shared_redirect_url', None))
        image_to_ascii_type = ImageToASCIIType.objects.get(generated_ascii=obj)
        image_to_ascii_options = ImageToASCIIOptions.objects.get(image_to_ascii_type=image_to_ascii_type)
        OutputASCII.objects.get(generated_ascii=obj, method_name='1')
        self.assertEqual(image_to_ascii_options.columns, '150')
        self.assertEqual(image_to_ascii_options.brightness, '50')
        self.assertEqual(image_to_ascii_options.contrast, '123')
        os.remove(image_to_ascii_type.input_image.path)
        obj.delete()


class TestAsciiReportView(TestCase):
    def _create_ascii_obj(self):
        file = open('_images/test/test_img_good.jpg', mode='rb')
        with open('_images/temporary/test_img_good.jpg', mode='wb') as file_new:
            file_new.write(file.read())
        file.close()
        response = self.client.post(reverse('ascii_share_url'), HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'preferred_output_method': '1',
                                          'file_name': 'test_img_good.jpg'})
        obj = GeneratedASCII.objects.first()
        return obj

    def _delete_ascii_obj(self, obj):
        image_to_ascii_type = ImageToASCIIType.objects.get(generated_ascii=obj)
        os.remove(image_to_ascii_type.input_image.path)
        image_to_ascii_type.delete()

    def test_non_ajax(self):
        """
        Non-ajax requests should return redirect 302
        """
        response = self.client.get(reverse('ascii_report_url', kwargs={'ascii_url_code': 'test'}))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse('ascii_report_url', kwargs={'ascii_url_code': 'test'}))
        self.assertEqual(response.status_code, 302)

    def test_ajax_get_request(self):
        """
        Ajax GET should return 405 not allowed
        """
        response = self.client.get(reverse('ascii_report_url', kwargs={'ascii_url_code': 'test'}),
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 405)

    def test_ajax_post_wrong_ascii_url_code(self):
        """
        Ajax POST with wrong ascii_url_code should return 400 and errors
        """
        response = self.client.post(reverse('ascii_report_url', kwargs={'ascii_url_code': 'test'}),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={})
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(json_content.get('errors', None))

    @mock.patch("captcha.fields.ReCaptchaField.validate")
    def test_ajax_success(self, mock):
        """
        Ajax POST with right data and capthca should return 200 and create new objects in database
        """
        obj = self._create_ascii_obj()
        response = self.client.post(reverse('ascii_report_url', kwargs={'ascii_url_code': obj.url_code}),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'text': 'testing text',
                                          'email': 'example@gmail.com'})
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(json_content.get('errors', None))
        report_obj = Report.objects.get(generated_ascii=obj)
        self.assertEqual(report_obj.text, 'testing text')
        self.assertEqual(report_obj.email, 'example@gmail.com')
        self._delete_ascii_obj(obj)

    @mock.patch("captcha.fields.ReCaptchaField.validate")
    def test_ajax_without_email(self, mock):
        """
        Ajax POST with right data and without email should return 200 and create new objects in database
        """
        obj = self._create_ascii_obj()
        response = self.client.post(reverse('ascii_report_url', kwargs={'ascii_url_code': obj.url_code}),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'text': 'testing text'})
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(json_content.get('errors', None))
        report_obj = Report.objects.get(generated_ascii=obj)
        self.assertEqual(report_obj.text, 'testing text')
        self.assertIsNone(report_obj.email)
        self._delete_ascii_obj(obj)

    @mock.patch("captcha.fields.ReCaptchaField.validate")
    def test_ajax_with_wrong_email(self, mock):
        """
        Ajax POST with right data but wrong email should return 400 with errors
        """
        obj = self._create_ascii_obj()
        response = self.client.post(reverse('ascii_report_url', kwargs={'ascii_url_code': obj.url_code}),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'text': 'testing text',
                                          'email': 'wrong email'})
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(json_content.get('errors', None))

    def test_ajax_without_captcha(self):
        """
        Ajax POST with right data but without captcha should return 400 with errors
        """
        obj = self._create_ascii_obj()
        response = self.client.post(reverse('ascii_report_url', kwargs={'ascii_url_code': obj.url_code}),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'text': 'testing text',
                                          'email': 'example@gmail.com'})
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(json_content.get('errors', None))

    @mock.patch("captcha.fields.ReCaptchaField.validate")
    def test_ajax_without_text(self, mock):
        """
        Ajax POST without text should return 400 with errors
        """
        obj = self._create_ascii_obj()
        response = self.client.post(reverse('ascii_report_url', kwargs={'ascii_url_code': obj.url_code}),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'email': 'example@gmail.com'})
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(json_content.get('errors', None))

    @mock.patch("captcha.fields.ReCaptchaField.validate")
    def test_ajax_with_text_beyond_limit(self, mock):
        """
        Ajax POST with text length > 1024 should return 400 with errors
        """
        obj = self._create_ascii_obj()
        response = self.client.post(reverse('ascii_report_url', kwargs={'ascii_url_code': obj.url_code}),
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                                    data={'text': 'a' * 1200,
                                          'email': 'example@gmail.com'})
        json_content = json.loads(response.content, encoding='utf-8')
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(json_content.get('errors', None))


class TestLanguageURLRedirectMiddleware(TestCase):
    def test_wrong_language(self):
        """
        If specified url is wrong, 404.
        """
        response = self.client.get('/jp123/about/')
        self.assertEqual(response.status_code, 404)

    def test_english_language(self):
        """
        If specified url is right, 200 and activate english language.
        """
        response = self.client.get('/en/about/')
        content = response.content.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Image to ASCII', content)
        self.assertIn('This project is made by', content)

    def test_russian_language(self):
        """
        If specified url is right, 200 and activate russian language.
        """
        response = self.client.get('/ru/about/')
        content = response.content.decode('utf-8')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Изображение в ASCII', content)
        self.assertIn('Этот проект сделал', content)

    def test_in_root_url(self):
        """
        Root url should work too.
        """
        response = self.client.get('/en')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/en/')
        self.assertEqual(response.status_code, 200)
