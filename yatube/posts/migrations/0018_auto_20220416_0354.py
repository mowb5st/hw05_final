# Generated by Django 2.2.6 on 2022-04-15 20:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_follow_pub_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-created']},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-created']},
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='pub_date',
            new_name='created',
        ),
        migrations.RenameField(
            model_name='follow',
            old_name='pub_date',
            new_name='created',
        ),
        migrations.RenameField(
            model_name='group',
            old_name='pub_date',
            new_name='created',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='pub_date',
            new_name='created',
        ),
    ]
