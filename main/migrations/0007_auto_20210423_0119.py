# Generated by Django 3.1 on 2021-04-22 19:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_comment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='movie',
            new_name='post',
        ),
    ]
