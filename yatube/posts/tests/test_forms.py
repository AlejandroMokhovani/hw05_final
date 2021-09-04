import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, Comment
from posts.forms import PostForm, CommentForm

User = get_user_model()

# Создаем временную папку для медиа-файлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
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

        # Создаем группы
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )

        cls.another_group = Group.objects.create(
            title='Другая тестовая группа',
            slug='another-test-slug',
            description='Другое тестовое описание группы'
        )
        # Создаем один пост
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.author,
            group=cls.group,
        )
        # Создаем один комментарий
        cls.comment_one = Comment.objects.create(
            text='First test comment',
            post=cls.post,
            author=cls.author,
        )

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Создаётся новая запись в базе данных."""

        # Подсчитаем количество постов
        posts_count = Post.objects.count()

        small_gif = (
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Тестовый текст добавленного поста',
            'group': self.group.id,
            'image': uploaded,
            # 'author': self.author
        }

        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, '/profile/auth_user/')
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст добавленного поста',
                group=self.group,
                author=self.user,
                image='posts/small.gif'
                ).exists()
        )


    def test_guest_cant_comment(self):
        """Неавторизованный клиент не может оставить комментарий к посту."""
        post = Post.objects.get(id=self.post.id)
        comments_count = post.comments.count()
        form_data = {
            'text': 'comment',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        # Проверяем, что количество комментариев не изменилось
        self.assertEqual(post.comments.count(), comments_count)


    def test_user_can_comment(self):
        """Авторизованный клиент может оставить комментарий к посту."""

        post = Post.objects.get(id=self.post.id)
        comments_count = post.comments.count()
        form_data = {
            'text': 'comment from authorized user',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        # Проверяем редирект
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        # Проверяем, что количество комментариев увеличилось на один
        self.assertEqual(post.comments.count(), comments_count + 1)
        # Пробуем найти наш комментарий
        self.assertTrue(
            post.comments.filter(
                text='comment from authorized user',
                ).exists()
        )


    def test_post_edit(self):
        """Происходит изменение поста в базе данных."""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Измененный текст',
            'group': self.another_group.id
        }

        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, '/posts/1/')

        # Проверяем, что количество постов не изменилось (не создался новый)
        self.assertEqual(Post.objects.count(), posts_count)

        # Проверяем что текст изменился
        self.assertIn(
            Post.objects.filter(text='Измененный текст')[0],
            Post.objects.all()
        )
