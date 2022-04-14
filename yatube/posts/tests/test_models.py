from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        post_text = ('Тестовая пост Тестовая пост Тестовая пост '
                     'Тестовая пост Тестовая пост Тестовая пост ')
        group_text = ('Тестовая группа Тестовая группа Тестовая группа '
                      'Тестовая группа Тестовая группа Тестовая группа ')
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title=group_text,
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=post_text,
        )

    def test_model_post_have_correct_object_names_(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        result = str(post)
        expected = post.text
        self.assertEqual(result, expected[:15])

    def test_model_group_have_correct_object_names_(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        post = PostModelTest.group
        result = str(post)
        expected = post.title
        self.assertEqual(result, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verbose_names = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        for field, expected_value in field_verbose_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)
