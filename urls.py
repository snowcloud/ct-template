""" urls.py for clintemplates app

"""

from django.conf.urls.defaults import *

urlpatterns = patterns('ct_template.views',
    (r'^$', 'index'),
    (r'^(?P<object_id>\d+)/$', 'detail'),
    (r'^(?P<object_id>\d+)/addreview/$', 'addreview'),
    (r'^(?P<object_id>\d+)/(?P<comment_id>\w+)/$', 'showcomment'),
    (r'^(?P<object_id>\d+)/(?P<comment_id>\w+)/comment/$', 'addcomment'),
)