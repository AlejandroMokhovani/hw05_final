from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_and_tech_pages(self):
        """Тестируем страницы автора и технологий."""
        urls_status_code = {
            '/about/author/': 200,
            '/about/tech/': 200,
        }
        for url, status_code in urls_status_code.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)
