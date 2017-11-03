# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-03 10:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20171102_2325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='archiving_state',
            field=models.CharField(blank=True, choices=[('ARCHIVED', 'Archived'), ('ARCHIVING', 'Archiving')], max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='preservation_state',
            field=models.CharField(blank=True, choices=[('PRESERVE', 'Should preserve this article'), ('STORED', 'Has been stored in order to be archived'), ('NO_PRESERVE', 'Preservation not required')], max_length=11),
        ),
    ]
