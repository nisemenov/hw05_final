# Generated by Django 4.2 on 2023-04-14 11:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_alter_post_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='group',
        ),
    ]
