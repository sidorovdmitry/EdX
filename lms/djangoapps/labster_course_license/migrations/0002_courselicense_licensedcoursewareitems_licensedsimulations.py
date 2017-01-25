# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import labster_course_license.models


class Migration(migrations.Migration):

    dependencies = [
        ('labster_course_license', '0001_fix_ccx_overrides'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseLicense',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_id', labster_course_license.models.CCXLocatorField(unique=True, max_length=255, db_index=True)),
                ('license_code', models.CharField(max_length=255, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='LicensedCoursewareItems',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('block', models.CharField(max_length=64)),
                ('licensed_simulations', models.TextField()),
                ('course_license', models.ForeignKey(to='labster_course_license.CourseLicense')),
            ],
        ),
        migrations.CreateModel(
            name='LicensedSimulations',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('licensed_simulations', models.TextField(null=True, blank=True)),
                ('course_license', models.ForeignKey(to='labster_course_license.CourseLicense')),
            ],
        ),
    ]
