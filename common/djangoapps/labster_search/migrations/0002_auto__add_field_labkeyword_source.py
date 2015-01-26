# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'LabKeyword.source'
        db.add_column('labster_search_labkeyword', 'source',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'LabKeyword.source'
        db.delete_column('labster_search_labkeyword', 'source')


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
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['labster.LanguageLab']", 'symmetrical': 'False'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'questions': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'quiz_block_file': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'quiz_block_last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'screenshot': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'screenshot_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '120', 'blank': 'True'}),
            'use_quiz_blocks': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'verified_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'wiki_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '120', 'blank': 'True'}),
            'xml_url_prefix': ('django.db.models.fields.CharField', [], {'default': "'https://labster.s3.amazonaws.com/unity/'", 'max_length': '255'})
        },
        'labster.languagelab': {
            'Meta': {'object_name': 'LanguageLab'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_code': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'language_name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'labster_search.labkeyword': {
            'Meta': {'unique_together': "(('lab', 'keyword', 'keyword_type'),)", 'object_name': 'LabKeyword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'keyword_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'lab': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['labster.Lab']"}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'source': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['labster_search']