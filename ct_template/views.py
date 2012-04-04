""" views for ct_template app

"""
import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.flatpages.models import FlatPage
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext, Context, Template
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect, HttpResponse
from django.forms import *
from django.http import Http404

from ct_framework.forms import ConfirmForm
from ct_groups.models import CTGroup
from ct_groups.decorators import check_permission
from ct_template.models import ClinTemplate, ClinTemplateReview, format_comment_url
from ct_template.forms import CTNewForm, ItemForm, ReviewForm, TemplateSettingsForm, NodeMetadataForm

TVIEWS = ['form', 'data', 'files', 'docs', 'metadata', 'settings']

try:
    from settings import DEFAULT_XML_MODEL
except ImportError:
    DEFAULT_XML_MODEL = '/new-template-default/'

def _get_tView(req, object):
    result = req.get('tView', 'form' if object.inf_model else 'docs')
    # fix for mangled URL in email, eg tView=3D3
    if result.startswith('3D'):
        result = result[2:]
    return result if result in TVIEWS else 'form'

def index(request):
    obj_list = ClinTemplate.objects.order_by('_template_id')
    return render_to_response('clintemplates_index.html', RequestContext( request, {'obj_list': obj_list, } ))

def detail(request, object_id):
    object = get_object_or_404(ClinTemplate, pk=object_id)
    if not check_permission(request.user, object.workgroup, 'resource', 'r'):
        return redirect_to_login(request.get_full_path())

    tView = _get_tView(request.GET, object)
    tNode = request.GET.get('tNode', None)
    tNode = '#%s' % tNode if tNode else ''
    settingsform = TemplateSettingsForm(instance=object)
    if request.is_ajax():
        base_t = "clintemplates_detail_base_blank.html"
    else:
        base_t = "clintemplates_detail_base.html"

    t = 'clintemplates_detail_dataset.html' if tView == 'data' else 'clintemplates_detail.html'
    
    return render_to_response(t, RequestContext( request,
        {'base_template': base_t, 'clin_template': object, 'tView': tView, 'tNode': tNode, 'settingsform': settingsform }))

@login_required
def settings_edit(request, object_id):
    """docstring for group_note"""
    object = get_object_or_404(ClinTemplate, pk=object_id)
    if not check_permission(request.user, object.workgroup, 'group', 'w'):
        raise PermissionDenied()

    if request.method == 'POST':
        result = request.POST.get('result')
        if result == 'cancel':
            return HttpResponseRedirect(reverse('template-detail',kwargs={'object_id':object.id}))
        settingsform = TemplateSettingsForm(request.POST, instance=object)
        if settingsform.is_valid():
            settingsform.save()
            messages.success(request, _('Your changes were saved.'))
            return HttpResponseRedirect('%s?tView=settings' % reverse('template-detail',kwargs={'object_id':object.id}))
    
    return HttpResponseRedirect('%s?tView=settings' % reverse('template-detail',kwargs={'object_id':object.id}))

@login_required
def new_template(request, group_slug):
    """docstring for new_template"""
    object = get_object_or_404(CTGroup, slug=group_slug)
    if not check_permission(request.user, object, 'resource', 'w'):
        raise PermissionDenied()

    if request.POST:
        if request.POST['result'] == _('Cancel'):
            return HttpResponseRedirect(object.get_absolute_url())
        else:
            form = CTNewForm(request.POST)
            if form.is_valid():
                label = form.cleaned_data['title']
                template_id = slugify(label)
                note = form.cleaned_data['text']

                defaults = { 'label': label, 'template_id': template_id, 'note': note }
                if object.template:
                    t = Template(object.template)
                    c = Context(defaults)
                    rendered = t.render(c)
                else:
                    try:
                        fp = FlatPage.objects.get(url=DEFAULT_XML_MODEL)
                        t = Template(fp.content)
                        c = Context(defaults)
                        rendered = t.render(c)
                    except FlatPage.DoesNotExist:
                        rendered = render_to_string('clintemplates_new.xml', defaults )
                ct = ClinTemplate(xmlmodel=rendered, workgroup=object, accept_reviews=False, enable_editing=True)                                
                ct.save()
                return HttpResponseRedirect(reverse('template-detail',kwargs={'object_id':ct.id}))
    else:
        form = CTNewForm()
        
    return render_to_response('clintemplates_new.html', 
        RequestContext( request, {'group': object, 'form': form }))

@login_required
def delete(request, object_id):
    """docstring for delete"""
    object = get_object_or_404(ClinTemplate, pk=object_id)
    if not check_permission(request.user, object.workgroup, 'resource', 'd'):
        raise PermissionDenied()

    if request.POST:
        if request.POST['result'] == _('Cancel'):
            return HttpResponseRedirect(object.get_absolute_url())
        else:
            form = ConfirmForm(request.POST)
            if form.is_valid():
                object.delete()
                return HttpResponseRedirect(reverse('group',kwargs={'group_slug': object.workgroup.slug}))
    else:
        form = ConfirmForm(initial={ 'resource_name': object.name })
    return render_to_response('ct_framework/confirm.html', 
        RequestContext( request, 
            {   'form': form,
                'title': _('Delete this %s?') % _(settings.SYNONYMS.get('Clinical template', 'Clinical template'))
            })
        )

@login_required
def edititem(request, object_id, view_id, item_id):
    object = get_object_or_404(ClinTemplate, pk=object_id)
    if not object.enable_editing:
        raise PermissionDenied()
    if not check_permission(request.user, object.workgroup, 'resource', 'w'):
        raise PermissionDenied()

    item = object.get_item(item_id)
    if item is None:
        raise Http404

    if request.POST:
        redirect_str = '%s?tView=%s' % (object.get_absolute_url(), view_id)
        if request.POST['result'] == _('Cancel'):
            return HttpResponseRedirect(redirect_str)
        else:
            form = ItemForm(request.POST)
            if form.is_valid():
                item.text = form.cleaned_data['text']
                object.save_model()
                return HttpResponseRedirect(redirect_str)
    else:
        form = ItemForm(initial={'title': item.get('label', "-"), 'text': item.text})
    
    return render_to_response('item_edit_text.html', 
        RequestContext( request, {'clin_template': object, 'form': form, 'tView': view_id }))

def showcomment(request, object_id, comment_id):
    object = get_object_or_404(ClinTemplate, pk=object_id)
    # TODO this does nothing if check fails
    # check and redirect to login of unauth, else deny
    if not check_permission(request.user, object.workgroup, 'resource', 'r') or \
        not check_permission(request.user, object.workgroup, 'comment', 'r'):
        return redirect_to_login(request.get_full_path())

    tView = _get_tView(request.GET, object)
    return render_to_response('clintemplates_detail.html', RequestContext( request, 
        {   'base_template': "clintemplates_detail_base.html", 'clin_template': object, 
            'comment_id': comment_id, 'tView': tView, 'settingsform': TemplateSettingsForm(instance=object)}))

@login_required
def addcomment(request, object_id, comment_id):
    object = get_object_or_404(ClinTemplate, pk=object_id)
    if not check_permission(request.user, object.workgroup, 'comment', 'w'):
        raise PermissionDenied()
    
    if request.POST:
        tView = _get_tView(request.POST, object)
        top_template_id = request.POST.get('top', '')
        if top_template_id == '':
            template_id = object_id
        else:
            template_id = top_template_id
        # abs_comment_id = '%s_%s_%s' % (object_id, tView, comment_id)
        # redirect_str = '%stemplates/%s/%s/?tView=%s#%s' % (settings.APP_BASE, template_id, abs_comment_id, tView, abs_comment_id)
        redirect_str = format_comment_url(object_id, template_id, tView, comment_id)
        if request.POST['result'] == _('Cancel'):
            return HttpResponseRedirect(redirect_str)
        else:
            comment_text = request.POST['comment_text']
            if comment_text == '':
                error_message = "Please type in your comment, or click 'Cancel'"
            elif not object.accept_comments:
                error_message = "This template does not accept comments. Please click 'Cancel'"
            else:
                object.add_comment(comment_id, comment_text, request.user)
                return HttpResponseRedirect(redirect_str)
    else:
        comment_text = ''
        error_message = ''
        tView = _get_tView(request.GET, object)
        top_template_id = request.GET.get('top', '')
    
    return render_to_response(
        'clintemplates_add_comment.html', 
        RequestContext( request, {
            'clin_template': object,
            'comment_id': comment_id,
            'error_message': error_message,
            'comment_text': comment_text,
            'tView': tView,
            'top_template_id': top_template_id            
            }))


@login_required
def addreview(request, object_id):
    object = get_object_or_404(ClinTemplate, pk=object_id)
    if not check_permission(request.user, object.workgroup, 'comment', 'w'):
        raise PermissionDenied()

    if request.method == 'POST':
        tView = _get_tView(request.POST, object)
        redirect_str = '%stemplates/%s/?tView=%s' % (settings.APP_BASE, object.id, tView)
        if request.POST['result'] == _('Cancel'):
            return HttpResponseRedirect(redirect_str)
        else:
            form = ReviewForm(request.POST)
            if form.is_valid():
                r = ClinTemplateReview()
                r.rating = str(form.clean()['rating'])
                r.review = str(form.clean()['review'])
                r.reviewer = request.user
                r.review_date = datetime.datetime.now()
                r.template = object
                r.is_public = True
                r.save()
                return HttpResponseRedirect(redirect_str)
    else:
        form = ReviewForm()
        form.ignore_errors = True
        #form.errors().clear()
        tView = _get_tView(request.GET, object)

    response = render_to_response('clintemplates_add_review.html',  
        RequestContext( request, { 'form': form, 'clin_template': object, 'tView': tView }) )
    return response

def get_node_metadata(request, object_id, node_id):
    object = get_object_or_404(ClinTemplate, pk=object_id)
    if not check_permission(request.user, object.workgroup, 'resource', 'r'):
        raise PermissionDenied()        
    # if request.is_ajax():
    node = object.get_item(node_id)
    # print node.attrib['description']
    return render_to_response('node_metadata.html', RequestContext( request,
        { 'elem': node, 'template': object }))

@login_required
def edit_node_metadata(request, object_id, node_id):
    object = get_object_or_404(ClinTemplate, pk=object_id)
    if not object.enable_editing:
        raise PermissionDenied()
    if not check_permission(request.user, object.workgroup, 'resource', 'w'):
        raise PermissionDenied()
    node = object.get_item(node_id)
    if node is None:
        raise Http404

    if request.POST:
        if request.POST['result'] == _('Cancel'):
            return HttpResponseRedirect('%s?tView=data&tNode=%s' % (object.get_absolute_url(), node_id))
        else:
            form = NodeMetadataForm(request.POST, instance=node, model=object)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('%s?tView=data&tNode=%s' % (object.get_absolute_url(), node_id))
    else:
        form = NodeMetadataForm(instance=node, model=object)

    return render_to_response('node_metadata_edit.html', 
        RequestContext( request, {'template': object, 'form': form }))

