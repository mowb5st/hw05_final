import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.group = Group.objects.create(
            title='Group title',
            slug='group_slug',
        )
        cls.group_second = Group.objects.create(
            title='Second Group title',
            slug='second_group_slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        for i in range(8):
            Post.objects.create(
                text=f'Пост для проверки {i * 1.37}',
                author=cls.user,
                group=cls.group,
            )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Валидная форма создает запись в Post."""
        text = 'Передаваемый текст'
        reverse_name = 'posts:profile'
        kwargs = {'username': self.user}
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
            'text': text,
            'group': self.group.pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        ordered_posts = Post.objects.all().order_by('-pk')[0]
        fields = {
            ordered_posts.text: form_data['text'],
            ordered_posts.group.pk: form_data['group'],
            ordered_posts.image: f'posts/{uploaded.name}',
        }
        for field, value in fields.items():
            with self.subTest():
                self.assertEqual(field, value)
        self.assertRedirects(response, reverse(
            reverse_name, kwargs=kwargs))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_edit(self):
        """Изменение поста через форму."""
        form_data = {
            'text': 'Измененный текст',
            'group': self.group_second.pk,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                id=self.post.pk
            ).exists()
        )

    def test_add_comment(self):
        """Валидная форма создает комментарий в Post."""
        form_data = {
            'text': 'Комментарий для теста'
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
        )
        self.assertTrue(
            Comment.objects.filter(
                post=self.post.pk,
                text=form_data['text'],
            ), 'Комментарий не найден'
        )
