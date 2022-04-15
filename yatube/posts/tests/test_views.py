import shutil
import tempfile
import time

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from yatube.settings import POSTS_LIMIT
from ..models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewTestBaseCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_slug_1',
            description='Тестовое описание',
        )
        Post.objects.create(
            author=cls.user,
            text='Пост 1',
            group=cls.group,
            image=cls.uploaded,
        )
        time.sleep(0.01)
        for i in range(14):
            cls.last_post = Post.objects.create(
                author=cls.user,
                text=f'Пост {i+1}',
                group=cls.group,
            )
            time.sleep(0.01)
        cls.first_post = Post.objects.get(id=1)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)


class ViewsTemplateTestCase(ViewTestBaseCase):

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse(
                'posts:index'),
            'posts/group_list.html': reverse('posts:group_list', kwargs={
                'slug': self.group.slug}),
            'posts/profile.html': reverse('posts:profile', kwargs={
                'username': self.user}),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={
                    'post_id': self.last_post.pk})),
            'posts/post_create.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class ViewsFormsTestCase(ViewTestBaseCase):

    def setUp(self) -> None:
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def template_for_context_tests(
            self, viewname, context_obj, index=None, kwargs=None):
        """Функция для проверки контекста страницы"""
        response = self.authorized_client.get(reverse(viewname, kwargs=kwargs))
        if None in {context_obj, index}:
            return response
        first_object = response.context.get(context_obj)[index]
        page_obj_fields = {
            first_object.pk: self.last_post.pk,
            first_object.text: self.last_post.text,
            first_object.author.pk: self.last_post.author.pk,
            first_object.author.username: self.last_post.author.username,
            first_object.group.pk: self.last_post.group.pk,
            first_object.group.title: self.last_post.group.title,
            first_object.image: self.last_post.image
        }
        for value, expected in page_obj_fields.items():
            with self.subTest():
                self.assertEqual(value, expected)
        return response

    def template_for_context_group_tests(
            self, viewname, context_obj, kwargs=None):
        """Функция для проверки контекста страницы"""
        response = self.authorized_client.get(reverse(viewname, kwargs=kwargs))
        group = response.context.get(context_obj)
        group_fields = {
            group.title: self.group.title,
            group.slug: self.group.slug,
            group.description: self.group.description,
            group.pk: self.group.pk,
        }
        for field, expected in group_fields.items():
            with self.subTest():
                self.assertEqual(field, expected)
        return response

    def template_for_form_tests(
            self, viewname, title, button, kwargs=None):
        """Функция для проверки формы страницы"""
        response = self.authorized_client.get(reverse(viewname, kwargs=kwargs))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        other_fields = {
            'title': title,
            'button': button,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        for value, expected in other_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(value)
                self.assertEqual(form_field, expected)
        return response

    def template_for_paginator_tests(
            self, viewname, kwargs=None):
        """Функция для проверки паджинатора страницы"""
        posts_on_second_page = Post.objects.count() - POSTS_LIMIT
        paginator_requests = {
            reverse(viewname, kwargs=kwargs): POSTS_LIMIT,
            reverse(viewname, kwargs=kwargs) + '?page=2': posts_on_second_page
        }
        for reverse_name, posts_count in paginator_requests.items():
            with self.subTest(reverse_name=reverse_name):
                reverse_name = self.authorized_client.get(
                    reverse_name).context.get('page_obj')
                self.assertEqual(len(reverse_name), posts_count)


class ViewsFormsTestUsesTemplates(ViewTestBaseCase):

    def setUp(self) -> None:
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_index_context(self):
        """Тест контекста страницы index"""
        response_index = 0
        reverse_name = 'posts:index'
        context_obj = 'page_obj'
        ViewsFormsTestCase.template_for_context_tests(
            self, reverse_name, context_obj, response_index)

    def test_post_index_paginator_collected(self):
        """Тест паджинатора первой и второй страницы index"""
        viewname = 'posts:index'
        ViewsFormsTestCase.template_for_paginator_tests(self, viewname)

    def test_group_list_context(self):
        """Тест контекста страницы group_list"""
        response_index = 0
        reverse_name = 'posts:group_list'
        context_obj = 'page_obj'
        group_obj = 'group'
        kwargs = {'slug': self.group.slug}
        ViewsFormsTestCase.template_for_context_tests(
            self, reverse_name, context_obj, response_index, kwargs)
        ViewsFormsTestCase.template_for_context_group_tests(
            self, reverse_name, group_obj, kwargs)

    def test_group_list_paginator_collected(self):
        """Тест паджинатора первой и второй страницы group_list"""
        viewname = 'posts:group_list'
        kwargs = {'slug': self.group.slug}
        ViewsFormsTestCase.template_for_paginator_tests(self, viewname, kwargs)

    def test_profile_context(self):
        """Тест контекста страницы profile"""
        posts_count_expected = 15
        response_index = 0
        reverse_name = 'posts:profile'
        context_obj = 'page_obj'
        kwargs = {'username': self.user}
        response = ViewsFormsTestCase.template_for_context_tests(
            self, reverse_name, context_obj, response_index, kwargs)
        a_posts_count = response.context.get('a_posts_count')
        self.assertEqual(a_posts_count, posts_count_expected)

    def test_profile_paginator_collected(self):
        """Тест паджинатора первой и второй страницы profile"""
        viewname = 'posts:profile'
        kwargs = {'username': self.user}
        ViewsFormsTestCase.template_for_paginator_tests(self, viewname, kwargs)

    def test_post_detail_context(self):
        """Тест контекста страницы posts_detail по id '1'"""
        template_post_id = 1
        total_author_posts = 15
        reverse_name = 'posts:post_detail'
        context_obj = 'post'
        kwargs = {'post_id': template_post_id}
        response = ViewsFormsTestCase.template_for_context_tests(
            self, reverse_name, context_obj, None, kwargs)
        post = response.context.get(context_obj)
        a_posts_count = response.context.get('a_posts_count')
        post_detail_context_fields = {
            post.pk: self.first_post.pk,
            post.text: self.first_post.text,
            post.author.username: self.first_post.author.username,
            post.group.title: self.first_post.group.title,
            post.group.pk: self.first_post.group.pk,
            post.image: self.first_post.image,
            a_posts_count: total_author_posts,
        }
        for field, expected in post_detail_context_fields.items():
            with self.subTest():
                self.assertEqual(field, expected)

    def test_post_edit_context(self):
        """Тест контекста страницы posts_edit и формы поста"""
        template_post_id = 1
        title = 'Редактировать пост'
        button = 'Сохранить'
        reverse_name = 'posts:post_edit'
        kwargs = {'post_id': template_post_id}
        response = ViewsFormsTestCase.template_for_form_tests(
            self, reverse_name, title, button, kwargs)
        form_field = response.context.get('is_edit')
        self.assertEqual(form_field, True)

    def post_edit_template(self):
        """posts:post_edit использует соответствующий шаблон"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.last_post.pk}))
        template = 'posts/post_create.html'
        self.assertTemplateUsed(response, template)

    def test_post_create_context(self):
        """Тест контекста страницы posts_create и формы поста"""
        title = 'Новый пост'
        button = 'Добавить'
        reverse_name = 'posts:post_create'
        ViewsFormsTestCase.template_for_form_tests(
            self, reverse_name, title, button)


class ViewsFormsPostCheckTestCase(ViewTestBaseCase):

    def setUp(self) -> None:
        super().setUp()
        title = 'Спец. группа'
        text = 'Текст поста'
        slug = 'spec_group'
        self.user_spec = User.objects.create(username='Special')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group_spec = Group.objects.create(
            title=title,
            slug=slug,
        )
        self.post_spec = Post.objects.create(
            author=self.user_spec,
            text=text,
            group=self.group_spec
        )

    def template_for_context_tests(
            self, viewname, context_obj, index=None, kwargs=None):
        """Функция для проверки контекста страницы"""
        response = self.authorized_client.get(reverse(viewname, kwargs=kwargs))
        if None in {context_obj, index}:
            return response
        page_obj = response.context.get(context_obj)[index]
        page_obj_fields = {
            page_obj.pk: self.post_spec.pk,
            page_obj.text: self.post_spec.text,
            page_obj.author.pk: self.post_spec.author.pk,
            page_obj.author.username: self.post_spec.author.username,
            page_obj.group.title: self.post_spec.group.title,
            page_obj.group.pk: self.post_spec.group.pk,
        }
        for field, expected in page_obj_fields.items():
            with self.subTest():
                self.assertEqual(field, expected)
        return response

    def test_post_spec_in_index(self):
        """Пост появился на главной странице"""
        response_index = 0
        reverse_name = 'posts:index'
        context_obj = 'page_obj'
        ViewsFormsPostCheckTestCase.template_for_context_tests(
            self, reverse_name, context_obj, response_index)

    def test_post_spec_in_group(self):
        """Пост появился в странице с группой"""
        response_index = 0
        reverse_name = 'posts:group_list'
        context_obj = 'page_obj'
        group_obj = 'group'
        kwargs = {'slug': self.group_spec.slug}
        response = ViewsFormsPostCheckTestCase.template_for_context_tests(
            self, reverse_name, context_obj, response_index, kwargs)
        group = response.context.get(group_obj)
        group_fields = {
            group.title: self.group_spec.title,
            group.slug: self.group_spec.slug,
            group.description: self.group_spec.description,
            group.pk: self.group_spec.pk,
        }
        for field, expected in group_fields.items():
            with self.subTest():
                self.assertEqual(field, expected)

    def test_post_spec_in_profile(self):
        """Пост появился на странице профиля"""
        response_index = 0
        reverse_name = 'posts:profile'
        context_obj = 'page_obj'
        kwargs = {'username': self.user_spec}
        ViewsFormsPostCheckTestCase.template_for_context_tests(
            self, reverse_name, context_obj, response_index, kwargs)


class CacheCheckTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='CachedUser')
        self.group = Group.objects.create(
            title='Cached Group',
            slug='cached-group',
            description='Описание Кэшированной группы',
        )
        text = 'testing cache'
        self.cached_post = Post.objects.create(
            author=self.user,
            text=text,
            group=self.group,
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cached_post(self):
        '''Создается пост, который будет проверяться при тесте кэша'''
        index = 0
        reverse_name = 'posts:index'
        context_obj = 'page_obj'
        response = self.authorized_client.get(reverse(
            reverse_name))
        first_object = response.context.get(context_obj)[index]
        post_detail_context_fields = {
            first_object.pk: self.cached_post.pk,
            first_object.text: self.cached_post.text,
            first_object.author.pk: self.cached_post.author.pk,
            first_object.author.username: self.cached_post.author.username,
            first_object.group.pk: self.cached_post.group.pk,
            first_object.group.title: self.cached_post.group.title,
            first_object.group.description: self.cached_post.group.description,
        }
        for field, expected in post_detail_context_fields.items():
            with self.subTest(cashed_post=self.cached_post):
                self.assertEqual(field, expected)

    def test_deleted_cached_post(self):
        '''Пост удаляется только после очистки кэша.'''
        reverse_name = 'posts:index'
        response = self.authorized_client.get(reverse(
            reverse_name)).content
        Post.objects.filter(id=self.cached_post.pk).delete()
        cached_response = self.authorized_client.get(reverse(
            reverse_name)).content
        cache.clear()
        refreshed_response = self.authorized_client.get(
            reverse(reverse_name)).content
        self.assertEqual(response, cached_response)
        self.assertNotEqual(cached_response, refreshed_response)


class SubsriptionTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_main = User.objects.create_user(username='Main User')
        cls.user_one = User.objects.create_user(username='First User')
        cls.user_two = User.objects.create_user(username='Second User')
        cls.user_three = User.objects.create_user(username='Third User')
        cls.group = Group.objects.create(
            title='Cached Group',
            slug='cached-group',
            description='Описание Кэшированной группы',
        )
        text_one = "first user's post"
        text_two = "second user's post"
        cls.post_one = Post.objects.create(
            author=cls.user_one,
            text=text_one,
            group=cls.group,
        )
        time.sleep(0.01)
        cls.unexpected_post = Post.objects.create(
            author=cls.user_three,
            text='Unexpected text',
            group=cls.group,
        )
        time.sleep(0.01)
        cls.post_two = Post.objects.create(
            author=cls.user_two,
            text=text_two,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_main)
        Follow.objects.create(user=self.user_main, author=self.user_one)
        Follow.objects.create(user=self.user_main, author=self.user_two)

    def test_sub_creatin_post_visibility(self):
        """Проверка появления постов подписки"""
        view_name = 'posts:follow_index'
        first_index = 0
        second_index = 1
        response = self.authorized_client.get(reverse(view_name))
        first_obj = response.context.get('page_obj')[first_index]
        second_obj = response.context.get('page_obj')[second_index]
        first_obj_fields = {
            first_obj.pk: self.post_two.pk,
            first_obj.text: self.post_two.text,
            first_obj.author.pk: self.post_two.author.pk,
            first_obj.author.username: self.post_two.author.username,
            first_obj.group.pk: self.post_two.group.pk,
            first_obj.group.title: self.post_two.group.title,
        }
        second_obj_fields = {
            second_obj.pk: self.post_one.pk,
            second_obj.text: self.post_one.text,
            second_obj.author.pk: self.post_one.author.pk,
            second_obj.author.username: self.post_one.author.username,
            second_obj.group.pk: self.post_one.group.pk,
            second_obj.group.title: self.post_one.group.title,
        }
        for value, expected in first_obj_fields.items():
            with self.subTest():
                self.assertEqual(value, expected)
        for value, expected in second_obj_fields.items():
            with self.subTest():
                self.assertEqual(value, expected)

    def test_sub_delition_post_visibility(self):
        """Проверка удаления постов подписки"""
        view_name = 'posts:follow_index'
        page_obj = 'page_obj'
        cached_response = self.authorized_client.get(reverse(
            view_name))
        count_of_cached_posts = len(cached_response.context[page_obj])
        sub_relationships = {
            self.user_one: self.user_main,
            self.user_two: self.user_main,
        }
        for author, user in sub_relationships.items():
            Follow.objects.filter(user=user, author=author).delete()
        refreshed_response = self.authorized_client.get(reverse(
            view_name))
        count_of_refreshed_posts = len(refreshed_response.context[page_obj])
        self.assertEqual(count_of_refreshed_posts, count_of_cached_posts - 2)

    def test_sub_posts_not_visible(self):
        """Посты не появились в ленте подписок другого пользователя"""
        self.authorized_client.force_login(self.user_three)
        viewname = 'posts:follow_index'
        context_obj = 'page_obj'
        expected_posts_count = 0
        response = self.authorized_client.get(reverse(viewname))
        posts_count = len(response.context.get(context_obj))
        self.assertEqual(posts_count, expected_posts_count)


class SubscriptionViewsTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_main = User.objects.create_user(username='Main User')
        cls.user_one = User.objects.create_user(username='First User')
        cls.user_two = User.objects.create_user(username='Second User')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_main)
        view_name = 'posts:profile_follow'
        kwargs = {'username': self.user_one}
        self.authorized_client.get(reverse(view_name, kwargs=kwargs))

    def test_sub_creation(self):
        """Проверка создания подписки"""
        expected_follow = Follow.objects.filter(
            user=self.user_main, author=self.user_one).exists()
        self.assertTrue(expected_follow)

    def test_sub_delition(self):
        """Проверка удаления подписки"""
        view_name_unfollow = 'posts:profile_unfollow'
        kwargs = {'username': self.user_one}
        expected_follow = Follow.objects.filter(
            user=self.user_main, author=self.user_one).exists()
        self.authorized_client.get(reverse(view_name_unfollow, kwargs=kwargs))
        expected_follow_deleted = Follow.objects.filter(
            user=self.user_main, author=self.user_one).exists()
        self.assertNotEqual(expected_follow, expected_follow_deleted)
