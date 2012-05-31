# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'ClinTemplate.show_data_view'
        db.add_column('ct_template_clintemplate', 'show_data_view', self.gf('django.db.models.fields.CharField')(default='show', max_length=12), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'ClinTemplate.show_data_view'
        db.delete_column('ct_template_clintemplate', 'show_data_view')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ct_groups.ctgroup': {
            'Meta': {'ordering': "['name']", 'object_name': 'CTGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'through': "orm['ct_groups.GroupMembership']", 'symmetrical': 'False'}),
            'moderate_membership': ('django.db.models.fields.CharField', [], {'default': "'closed'", 'max_length': '8'}),
            'moderated_message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'resource_comment_order': ('django.db.models.fields.CharField', [], {'default': "u'oldest first'", 'max_length': '12'}),
            'show_discussion': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_resources': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_template_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'tags': ('tagging.fields.TagField', [], {'default': "''"}),
            'template': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'ct_groups.groupmembership': {
            'Meta': {'object_name': 'GroupMembership'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ct_groups.CTGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_editor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_manager': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'moderation': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['ct_groups.Moderation']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'post_updates': ('django.db.models.fields.CharField', [], {'default': "'single'", 'max_length': '8'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'accepted'", 'max_length': '8'}),
            'tool_updates': ('django.db.models.fields.CharField', [], {'default': "'single'", 'max_length': '8'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'ct_groups.moderation': {
            'Meta': {'object_name': 'Moderation'},
            'applicants_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_requested': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moderation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'moderator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'response_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '8'})
        },
        'ct_template.clintemplate': {
            'Meta': {'ordering': "['_template_id']", 'object_name': 'ClinTemplate'},
            '_template_id': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '64', 'blank': 'True'}),
            'accept_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'accept_reviews': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'enable_editing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_voting': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'included_templates': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'in_templates'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['ct_template.ClinTemplate']"}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_data_view': ('django.db.models.fields.CharField', [], {'default': "'show'", 'max_length': '12'}),
            'tags': ('tagging.fields.TagField', [], {'default': "''"}),
            'workgroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ct_groups.CTGroup']"}),
            'xmlmodel': ('django.db.models.fields.TextField', [], {})
        },
        'ct_template.clintemplatereview': {
            'Meta': {'ordering': "['review_date']", 'object_name': 'ClinTemplateReview'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'rating': ('django.db.models.fields.SmallIntegerField', [], {}),
            'review': ('django.db.models.fields.TextField', [], {}),
            'review_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 5, 31, 0, 41, 37, 815999)', 'null': 'True'}),
            'reviewer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ct_template.ClinTemplate']", 'null': 'True'})
        }
    }

    complete_apps = ['ct_template']
