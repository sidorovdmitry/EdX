# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Problem.lab'
        db.delete_column('labster_adaptive_problem', 'lab_id')

        # Adding field 'Problem.order'
        db.add_column('labster_adaptive_problem', 'order',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Problem.image_url'
        db.add_column('labster_adaptive_problem', 'image_url',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=500, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Problem.lab'
        db.add_column('labster_adaptive_problem', 'lab',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['labster.Lab'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Problem.order'
        db.delete_column('labster_adaptive_problem', 'order')

        # Deleting field 'Problem.image_url'
        db.delete_column('labster_adaptive_problem', 'image_url')


    models = {
        'labster_adaptive.answer': {
            'Meta': {'object_name': 'Answer'},
            'answer': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'difficulty': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_correct': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'problem': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['labster_adaptive.Problem']"})
        },
        'labster_adaptive.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'labster_adaptive.problem': {
            'Meta': {'object_name': 'Problem'},
            'answer_type': ('django.db.models.fields.IntegerField', [], {}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['labster_adaptive.Category']", 'symmetrical': 'False', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'discrimination': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'feedback': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'guessing': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'item_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'modified_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'number_of_destractors': ('django.db.models.fields.IntegerField', [], {}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'question': ('django.db.models.fields.TextField', [], {}),
            'scales': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['labster_adaptive.Scale']", 'symmetrical': 'False', 'blank': 'True'}),
            'sd_time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        },
        'labster_adaptive.scale': {
            'Meta': {'object_name': 'Scale'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['labster_adaptive']