from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class StaticURLTestsCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='temp_group',
            slug='temp_group_slug',
        )
        cls.post = Post.objects.create(
            text='post text',
            author=cls.user,
            group=cls.group,
        )
        cls.post_create_template = 'posts/post_create.html'
        cls.index = ''
        cls.group_adress = f'/group/{cls.group.slug}/'
        cls.profile_adress = f'/profile/{cls.user}/'
        cls.post_detail_adress = f'/posts/{cls.post.pk}/'
        cls.post_edit_adress = f'/posts/{cls.post.pk}/edit/'
        cls.post_create_adress = '/create/'
        cls.about_author_adress = '/about/author/'
        cls.about_tech_adress = '/about/tech/'

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_templates(self):
        """URL страницы использует правильный шаблон"""
        templates_url_names = {
            'posts/index.html': self.index,
            'posts/group_list.html': self.group_adress,
            'posts/profile.html': self.profile_adress,
            'posts/post_detail.html': self.post_detail_adress,
            'posts/post_create.html': self.post_edit_adress,
            self.post_create_template: self.post_create_adress,
            'about/author.html': self.about_author_adress,
            'about/tech.html': self.about_tech_adress,
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_url_for_guest(self):
        """Cтраницы, доступные всем"""
        status_url_names = {
            self.index,
            self.group_adress,
            self.profile_adress,
            self.post_detail_adress,
        }
        for adress in status_url_names:
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_for_author(self):
        """Cтраницы, доступные автору"""
        response = self.authorized_client.get(self.post_edit_adress)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_status_ok(self):
        """Cтраницы, доступные авторизованному пользователю"""
        response = self.authorized_client.get(self.post_create_adress)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_status_not_found(self):
        """Статус несуществующей страницы возвращает код 404"""
        adress = '/unexisting_page/'
        response = self.authorized_client.get(adress)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
