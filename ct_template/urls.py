""" urls.py for clintemplates app

"""

from django.conf.urls.defaults import *

from ct_groups.decorators import group_perm
from ct_template.views import new_template

resource_write = group_perm('resource', 'w')

urlpatterns = patterns('ct_template.views',
    url(r'^$', 'index'),
    url(r'^(?P<object_id>\d+)/$', 'detail', name="template-detail"),
    url(r'^(?P<object_id>\d+)/addreview/$', 'addreview'),
    url(r'^(?P<object_id>\d+)/delete/$', 'delete', name="template-delete"),
    url(r'^(?P<object_id>\d+)/settings/$', 'settings_edit', name="template-settings"),
    url(r'^(?P<object_id>\d+)/node-metadata/(?P<node_id>\w+)/edit/$', 'edit_node_metadata', name="edit-node-metadata"),
    url(r'^(?P<object_id>\d+)/node-metadata/(?P<node_id>\w+)/$', 'get_node_metadata', name="node-metadata"),
    url(r'^(?P<object_id>\d+)/(?P<comment_id>\w+)/$', 'showcomment'),
    url(r'^(?P<object_id>\d+)/(?P<comment_id>\w+)/comment/$', 'addcomment'),
    url(r'^(?P<object_id>\d+)/(?P<view_id>\w+)/(?P<item_id>\w+)/edit/$', 'edititem', name="template-item-edit"),
    url(r'^(?P<group_slug>[^/]+)/new-ct/', resource_write(new_template), name='new-ct'),

)