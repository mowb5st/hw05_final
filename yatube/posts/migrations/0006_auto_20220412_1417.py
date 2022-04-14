# Generated by Django 2.2.6 on 2022-04-12 07:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_auto_20220412_0307'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Напишите комментарий', verbose_name='Текст комментария')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_author', to='posts.Post')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.Post')),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='comment',
            field=models.ForeignKey(blank=True, help_text='Комментарий к посту', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Comment', to='posts.Comment', verbose_name='Комментарий'),
        ),
    ]
