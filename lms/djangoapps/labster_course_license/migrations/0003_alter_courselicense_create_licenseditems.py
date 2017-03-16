# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import xmodule_django.models
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('labster_course_license', '0002_add_courselicense'),
    ]

    operations = [
        migrations.CreateModel(
            name='LicensedCoursewareItems',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('block', xmodule_django.models.UsageKeyField(max_length=255, db_index=True)),
                ('simulations', django_extensions.db.fields.json.JSONField()),
            ],
        ),
        migrations.AddField(
            model_name='courselicense',
            name='simulations',
            field=django_extensions.db.fields.json.JSONField()
        ),
    ]
