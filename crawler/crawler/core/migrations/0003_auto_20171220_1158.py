# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-20 11:58
from __future__ import unicode_literals

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20171128_1541'),
    ]

    database_operations = [
        migrations.AlterModelTable(
            'PriorityTag',
            'scraping_prioritytag'
        ),
        migrations.AlterModelTable(
            'ReleaseDateTag',
            'scraping_releasedatetag'
        ),
        migrations.AlterModelTable(
            'NotFoundOnlyTag',
            'scraping_notfoundonlytag'
        )
    ]

    state_operations = [
        migrations.DeleteModel('PriorityTag'),
        migrations.DeleteModel('ReleaseDateTag'),
        migrations.DeleteModel('NotFoundOnlyTag')
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations)
    ]
