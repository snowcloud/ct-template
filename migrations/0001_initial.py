# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ClinTemplate'
        db.create_table('ct_template_clintemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('_template_id', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=64, unique=True, blank=True)),
            ('xmlmodel', self.gf('django.db.models.fields.TextField')()),
            ('workgroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ct_groups.CTGroup'])),
            ('tags', self.gf('tagging.fields.TagField')()),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('accept_comments', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('ct_template', ['ClinTemplate'])

        # Adding M2M table for field included_templates on 'ClinTemplate'
        db.create_table('ct_template_clintemplate_included_templates', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_clintemplate', models.ForeignKey(orm['ct_template.clintemplate'], null=False)),
            ('to_clintemplate', models.ForeignKey(orm['ct_template.clintemplate'], null=False))
        ))
        db.create_unique('ct_template_clintemplate_included_templates', ['from_clintemplate_id', 'to_clintemplate_id'])

        # Adding model 'ClinTemplateReview'
        db.create_table('ct_template_clintemplatereview', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reviewer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('review_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2010, 4, 11, 18, 56, 20, 834163), null=True)),
            ('rating', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('review', self.gf('django.db.models.fields.TextField')()),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['ct_template.ClinTemplate'], null=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('ct_template', ['ClinTemplateReview'])


    def backwards(self, orm):
        
        # Deleting model 'ClinTemplate'
        db.delete_table('ct_template_clintemplate')

        # Removing M2M table for field included_templates on 'ClinTemplate'
        db.delete_table('ct_template_clintemplate_included_templates')

        # Deleting model 'ClinTemplateReview'
        db.delete_table('ct_template_clintemplatereview')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'ct_groups.ctgroup': {
            'Meta': {'object_name': 'CTGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'through': "orm['ct_groups.GroupMembership']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'unique': 'True', 'db_index': 'True'}),
            'tags': ('tagging.fields.TagField', [], {})
        },
        'ct_groups.groupmembership': {
            'Meta': {'object_name': 'GroupMembership'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ct_groups.CTGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_editor': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_manager': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'moderation': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '8'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'post_updates': ('django.db.models.fields.CharField', [], {'default': "'single'", 'max_length': '8'}),
            'tool_updates': ('django.db.models.fields.CharField', [], {'default': "'single'", 'max_length': '8'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'ct_template.clintemplate': {
            'Meta': {'object_name': 'ClinTemplate'},
            '_template_id': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '64', 'unique': 'True', 'blank': 'True'}),
            'accept_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'included_templates': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'in_templates'", 'blank': 'True', 'null': 'True', 'to': "orm['ct_template.ClinTemplate']"}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'workgroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ct_groups.CTGroup']"}),
            'xmlmodel': ('django.db.models.fields.TextField', [], {})
        },
        'ct_template.clintemplatereview': {
            'Meta': {'object_name': 'ClinTemplateReview'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'rating': ('django.db.models.fields.SmallIntegerField', [], {}),
            'review': ('django.db.models.fields.TextField', [], {}),
            'review_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 4, 11, 18, 56, 20, 834163)', 'null': 'True'}),
            'reviewer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ct_template.ClinTemplate']", 'null': 'True'})
        }
    }

    complete_apps = ['ct_template']
