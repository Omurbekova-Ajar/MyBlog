# Generated by Django 3.1 on 2021-04-22 11:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_rating'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rating',
            old_name='movie',
            new_name='post',
        ),
    ]
