# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import xmodule_django.models
import django_extensions.db.fields.json
import labster_course_license.models


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
                ('simulations', django_extensions.db.fields.json.JSONField(help_text=b'List of block licensed simulations, stored as json string value')),
            ],
        ),
        migrations.AlterField(
            model_name='courselicense',
            name='course_id',
            field=labster_course_license.models.CCXLocatorField(unique=True, max_length=255, db_index=True),
        ),
        migrations.AddField(
            model_name='courselicense',
            name='simulations',
            field=django_extensions.db.fields.json.JSONField(help_text=b'List of course licensed simulations, stored as json string value')
        ),
        migrations.AddField(
            model_name='courselicense',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='courselicense',
            name='modified_at',
            field=models.DateTimeField(auto_now=True, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='licensedcoursewareitems',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='licensedcoursewareitems',
            name='modified_at',
            field=models.DateTimeField(auto_now=True, null=True),
            preserve_default=False,
        ),
    ]
