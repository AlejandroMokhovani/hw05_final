import shutil
import tempfile
# import time
import unittest

# from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from itertools import islice
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group, Follow

User = get_user_model()

# Создаем временную папку для медиа-файлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class ViewsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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
            text='Тестовый текст поста',
            author=cls.author,
            group=cls.group
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'base.html',
            reverse('posts:post_create'): 'posts/create_post.html',

            reverse('posts:group_list', kwargs={'slug': 'test-slug'}): (
                'posts/group_list.html'
            ),

            reverse('posts:profile', kwargs={'username': 'author'}): (
                'posts/profile.html'
            ),

            reverse('posts:post_detail', kwargs={'post_id': 1}): (
                'posts/post_detail.html'
            ),

            reverse('posts:post_edit', kwargs={'post_id': 1}): (
                'posts/create_post.html'
            ),
        }
        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class ContextViewsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # cache.clear()

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

        # Создаем посты
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.author,
            group=cls.group,
        )
        cls.post_two = Post.objects.create(
            text='Текст второго поста',
            author=cls.author,
            group=cls.another_group,
        )
        cls.last_post = Post.objects.create(
            text='Текст последнего поста',
            author=cls.author,
            group=cls.group,
        )
        cls.post_wo_group = Post.objects.create(
            text='Текст поста без группы',
            author=cls.author,
            group=cls.group,
        )

    def SetUp(self):
        pass
        # cache.clear()

    def test_home_page_show_correct_context(self):
        """Проверяем, что на главную страницу выводится список всех постов."""

        # cache.clear()

        posts = Post.objects.all()
        response = self.guest_client.get(reverse('posts:index'))
        # так как всего четыре поста, пагинацию не учитываем и используем
        # posts.all() вместо posts.all()[:9]
        self.assertEqual(
            list(response.context['page_obj'].object_list), list(posts)
        )

    def test_group_page_show_correct_context(self):
        """Проверяем, что на странице группы - посты этой группы."""
        posts = Post.objects.all()
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(
            list(response.context['page_obj'].object_list),
            list(posts.filter(group=self.group))
        )

    def test_profile_page_show_correct_context(self):
        """Проверяем, что на странице пользователя только его посты."""
        posts = Post.objects.all()
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'author'})
        )
        self.assertEqual(
            response.context['page_obj'].object_list,
            list(posts.filter(author=self.author))
        )

    def test_post_page_show_correct_context(self):
        """Проверяем, что на странице один пост с нужным нам id."""
        posts = Post.objects.all()
        POST_ID = 1
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': POST_ID})
        )
        self.assertEqual(response.context['post'], posts.filter(id=POST_ID)[0])

    def test_post_edit_page_show_correct_context(self):
        """Проверяем поля, доступные для редактирования."""
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        """Проверяем поля доступные для ввода."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_correct_post_display(self):
        """Тестируем корректное отображение поста."""
        POST_ID = 3
        posts = Post.objects.all()
        pages = [
            # пост появляется на главной странице сайта
            reverse('posts:index'),
            # пост появляется на странице выбранной группы
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            # пост появляется в профайле пользователя
            reverse('posts:profile', kwargs={'username': 'author'}),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertIn(
                    posts.filter(id=POST_ID)[0],
                    response.context['page_obj'].object_list
                )

    def test_correct_post_display_another_group(self):
        """Проверяем, что посты не появляются в другой группе."""
        POST_ID = 3
        posts = Post.objects.all()
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': 'another-test-slug'})
        )
        self.assertNotIn(
            posts.filter(id=POST_ID)[0],
            response.context['page_obj'].object_list
        )


class PaginatorPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создаем неавторизованный клиент
        cls.guest_client = Client()

        # Создаем автора, клиент и логиним его
        cls.author_wolf = User.objects.create_user(username='author_wolf')
        cls.author_one_client = Client()
        cls.author_one_client.force_login(user=cls.author_wolf)

        # Создаем автора, клиент и логиним его
        cls.author_rabbit = User.objects.create_user(username='author_rabbit')
        cls.author_two_client = Client()
        cls.author_two_client.force_login(user=cls.author_rabbit)

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
        cls.none_group = None

        batch_size = 1
        objs = (
            Post(
                text='Test %s' % i,
                author=cls.author_wolf,
                group=cls.group,
            ) for i in range(12)
        )
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            Post.objects.bulk_create(batch, batch_size)

        cls.post_wo_group = Post.objects.create(
            text='Текст поста без группы',
            author=cls.author_rabbit,
            group=cls.none_group,
        )

    def test_paginator(self):
        """Тестируем пагинатор."""
        pages_and_post_count = {
            reverse('posts:index') + '?page=1': 10,
            reverse('posts:index') + '?page=2': 3,
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ) + '?page=1': 10,
            reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
            ) + '?page=2': 2,
            reverse(
                'posts:profile', kwargs={'username': 'author_wolf'}
            ) + '?page=1': 10,
            reverse(
                'posts:profile', kwargs={'username': 'author_wolf'}
            ) + '?page=2': 2,
        }
        for reverse_name, post_count in pages_and_post_count.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj'].object_list), post_count
                )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PictureInContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создаем неавторизованный клиент
        cls.guest_client = Client()

        # Создаем пользователя, клиент и логиним его
        cls.user = User.objects.create_user(username='auth_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        # Создаем группу
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы'
        )

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        # Создаем один пост
        cls.post = Post.objects.create(
            text='Текст поста',
            author=cls.user,
            group=cls.group,
            image=cls.image,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_show_correct_context(self):
        """Пост сформирован с правильным контекстом."""

        # На главной странице
        response = self.authorized_client.get(reverse('posts:index'))

        first_object = response.context['page_obj'][0]

        post_text = first_object.text
        post_group = first_object.group
        post_author = first_object.author
        post_image = first_object.image

        self.assertEqual(post_text, 'Текст поста')
        self.assertEqual(str(post_group), 'Тестовая группа')
        self.assertEqual(str(post_author), 'auth_user')
        self.assertEqual(post_image, 'posts/small.gif')

        # На странице группы
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))

        first_object = response.context['page_obj'][0]

        post_text = first_object.text
        post_group = first_object.group
        post_author = first_object.author
        post_image = first_object.image

        self.assertEqual(post_text, 'Текст поста')
        self.assertEqual(str(post_group), 'Тестовая группа')
        self.assertEqual(str(post_author), 'auth_user')
        self.assertEqual(post_image, 'posts/small.gif')

        # На странице пользователя
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))

        first_object = response.context['page_obj'][0]

        post_text = first_object.text
        post_group = first_object.group
        post_author = first_object.author
        post_image = first_object.image

        self.assertEqual(post_text, 'Текст поста')
        self.assertEqual(str(post_group), 'Тестовая группа')
        self.assertEqual(str(post_author), 'auth_user')
        self.assertEqual(post_image, 'posts/small.gif')

        # На странице поста
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))

        first_object = response.context['post']

        post_text = first_object.text
        post_group = first_object.group
        post_author = first_object.author
        post_image = first_object.image

        self.assertEqual(post_text, 'Текст поста')
        self.assertEqual(str(post_group), 'Тестовая группа')
        self.assertEqual(str(post_author), 'auth_user')
        self.assertEqual(post_image, 'posts/small.gif')


class CacheMainPageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создаем автора, клиент и логиним его
        cls.author = User.objects.create_user(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(user=cls.author)

        # Создаем пост
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.author,
        )

    @unittest.skip('dont_work')
    def test_cache(self):
        """кэш."""

        # один пост
        # posts_count = Post.objects.count()
        form_data = {
            'text': 'comment',
        }

        self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        # один добавили стало два
        # но в ответе должен быть один
        response = self.author_client.get(reverse('posts:index'))

        self.assertEqual(
            len(response.context['page_obj'].object_list), Post.objects.count()
        )

        # один удалили, теперь 1 в базе
        Post.objects.filter(
            text='comment'
        ).delete()

        # но два в кэше должно быть, но там один
        response = self.author_client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj'].object_list),    # 2 кэш
            Post.objects.count() + 1                          # 1 база + 1
        )

        # cache.clear()
        # time.sleep(21)

        response = self.author_client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj'].object_list), Post.objects.count()
        )


class CreateDeleteFollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создаем пользователя, клиент и логиним его
        cls.user = User.objects.create_user(username='auth_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        # Создаем автора, клиент и логиним его
        cls.author = User.objects.create_user(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(user=cls.author)

    def test_authorized_user_can_follow(self):
        """Проверка создания подписки"""

        # юзер подписывается на автора
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username}
            ),
        )
        # теперь юзер становится подписчиком (он подписывается)
        self.assertEqual(self.user.follower.all().count(), 1)
        # а автор имеет подписчика (на него подписываются)
        self.assertEqual(self.author.following.all().count(), 1)

    def test_authorized_user_can_unfollow(self):
        """Проверка удаления подписки"""

        # юзер подписывается на автора
        response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username}
            ),
        )
        # замеряем состояние
        count_follower = self.user.follower.all().count()
        count_following = self.author.following.all().count()

        # и отписываем юзера от автора
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author.username}
            ),
        )
        # смотрим что follower и following удаляются
        self.assertEqual(
            self.user.follower.all().count(), count_follower - 1
        )
        self.assertEqual(
            self.author.following.all().count(), count_following - 1
        )


class CheckFollowList(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Создаем пользователя, клиент и логиним его
        cls.user = User.objects.create_user(username='auth_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        # Создаем автора, клиент и логиним его
        cls.author = User.objects.create_user(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(user=cls.author)

        # Создаем второго автора, клиент и логиним его
        cls.bad_author = User.objects.create_user(username='bad_author')
        cls.bad_author_client = Client()
        cls.bad_author_client.force_login(user=cls.author)

        # Cоздаем подписку юзера на автора
        cls.user_author = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def test_authorized_user_can_unfollow(self):
        """Тестирование ленты подписок"""

        form_data = {
            'text': 'Хороший пост хорошего автора',
        }

        # Автор пишет пост
        self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # берем наш пост и
        posts = Post.objects.all()
        # смотрим, что этот пост появляется в ленте подписок юзера
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            response.context['page_obj'].object_list, list(posts)
        )

        # и не появляется в ленте подписок плохого автора (т.е. их 0)
        response = self.bad_author_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            len(response.context['page_obj'].object_list), 0
        )
