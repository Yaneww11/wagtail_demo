# Generated by Django 5.1.7 on 2025-03-31 09:54

import modelcluster.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_blogpagegalleryimage'),
        ('snippets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpage',
            name='authors',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='snippets.author'),
        ),
    ]
