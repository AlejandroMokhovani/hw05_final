from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self):
        """Проверяем доступность главной страницы."""
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создаем неавторизованный клиент
        cls.guest_client = Client()

        # Создаем пользователя, клиент и логиним его
        cls.user = User.objects.create_user(username='auth_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        # Создаем автора, клиент и логиним его
        cls.author = User.objects.create_user(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(user=cls.author)

        # Создаем группу
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )
        # Создаем пост
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.author,
            group=cls.group
        )

    def test_urls_guest_client(self):
        """Проверка доступа для неавторизованного пользователя."""
        status_code_for_urls = {
            '/': 200,
            '/group/test-slug/': 200,
            '/profile/author/': 200,
            '/create/': 302,
            '/posts/1/': 200,
            '/posts/1/edit/': 302,
            '/unexisting_page/': 404,
        }
        for url, status_code in status_code_for_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_guest_client_redirect(self):
        """Проверка редиректa для неавторизованного пользователя."""
        status_code_for_urls = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
        }
        for url, status_code in status_code_for_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, status_code)

    def test_urls_authorized_client(self):
        """Проверка доступа для авторизованного пользователя."""
        status_code_for_urls = {
            '/': 200,
            '/group/test-slug/': 200,
            '/profile/author/': 200,
            '/create/': 200,
            '/posts/1/': 200,
            '/posts/1/edit/': 302,
            '/unexisting_page/': 404,
        }
        for url, status_code in status_code_for_urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_authorized_client_redirect(self):
        """Проверка редиректа для авторизованного пользователя."""
        response = self.authorized_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/posts/1/')

    def test_urls_author(self):
        """Проверка доступа для автора."""
        status_code_for_urls = {
            '/': 200,
            '/group/test-slug/': 200,
            '/profile/author/': 200,
            '/create/': 200,
            '/posts/1/': 200,
            '/posts/1/edit/': 200,
            '/unexisting_page/': 404,
        }
        for url, status_code in status_code_for_urls.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_html(self):
        """Проверка вызываемых html-шаблонов."""
        cache.clear()
        templates_url_names = {
            '/': 'index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/author/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.author_client.get(adress)
                self.assertTemplateUsed(response, template)
