""" urls.py for clintemplates app

"""

from django.conf.urls.defaults import *

urlpatterns = patterns('ct_template.views',
    url(r'^$', 'index'),
    url(r'^(?P<object_id>\d+)/$', 'detail', name="template-detail"),
    url(r'^(?P<object_id>\d+)/addreview/$', 'addreview'),
    url(r'^(?P<object_id>\d+)/(?P<comment_id>\w+)/$', 'showcomment'),
    url(r'^(?P<object_id>\d+)/(?P<comment_id>\w+)/comment/$', 'addcomment'),
    url(r'^(?P<object_id>\d+)/(?P<view_id>\w+)/(?P<item_id>\w+)/edit/$', 'edititem', name="template-item-edit"),
)