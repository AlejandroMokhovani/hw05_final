from django.test import Client, TestCase


class ViewTestClass(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создаем неавторизованный клиент
        cls.guest_client = Client()

    def test_status_code_nonexist_page(self):
        """Проверка статус кода несуществующей страницы."""
        response = self.guest_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)

    def test_template_nonexist_page(self):
        """Передача правильного шаблона для несуществующей страницы."""
        response = self.guest_client.get('/nonexist-page/')
        self.assertTemplateUsed(response, 'core/404.html')
