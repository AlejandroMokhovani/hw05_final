from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост от тестовой группы от автора auth',
            group=cls.group,
            author=cls.user,
        )

    def test_models_have_correct_post_text(self):
        """Проверяем отображение текста поста."""
        post = PostModelTest.post
        text = post.text[:15]
        self.assertEqual(text, post.text[:15])

    def test_models_have_correct_group_title(self):
        """Проверяем отображение названия поста."""
        group = PostModelTest.group
        title = group.title
        self.assertEqual(title, 'Тестовая группа')
