# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DemoCourse'
        db.create_table('labster_frontend_democourse', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('course_id', self.gf('xmodule_django.models.CourseKeyField')(unique=True, max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(default='', max_length=255, db_index=True, blank=True)),
            ('lab', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['labster.Lab'], null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('labster_frontend', ['DemoCourse'])


    def backwards(self, orm):
        # Deleting model 'DemoCourse'
        db.delete_table('labster_frontend_democourse')


    models = {
        'labster.lab': {
            'Meta': {'object_name': 'Lab'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'demo_course_id': ('xmodule_django.models.CourseKeyField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'engine_file': ('django.db.models.fields.CharField', [], {'default': "'labster.unity3d'", 'max_length': '128', 'blank': 'True'}),
            'engine_xml': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'quiz_block_file': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'quiz_block_last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'use_quiz_blocks': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'verified_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'xml_url_prefix': ('django.db.models.fields.CharField', [], {'default': "'https://labster.s3.amazonaws.com/unity/'", 'max_length': '255'})
        },
        'labster_frontend.democourse': {
            'Meta': {'object_name': 'DemoCourse'},
            'course_id': ('xmodule_django.models.CourseKeyField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'lab': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['labster.Lab']", 'null': 'True', 'blank': 'True'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'slug': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'db_index': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['labster_frontend']