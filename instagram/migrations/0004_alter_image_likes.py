# Generated by Django 3.2.6 on 2021-09-15 08:41

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instagram', '0003_alter_image_likes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='likes',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=None),
        ),
    ]