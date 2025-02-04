from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts')
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text[:15]


class Group(CreatedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(
        unique=True,
        verbose_name='URL')
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Напишите комментарий',
    )

    class Meta:
        ordering = ['-created']

    def __str__(self) -> str:
        return self.text


class Follow(CreatedModel):

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        help_text='Пользователь, который подписывается',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='На кого подписался',
        related_name='following',
        help_text='Пользователь, на которого подписываются',
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'subsription'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_following')
        ]
