""" views for ct_template app

"""
import datetime

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext, Context, Template
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import *
from django.http import Http404

from ct_framework.forms import ConfirmForm
from ct_groups.models import CTGroup
from ct_groups.decorators import check_permission
from ct_template.models import ClinTemplate, ClinTemplateReview, format_comment_url
from ct_template.forms import CTNewForm, ItemForm, ReviewForm, TemplateSettingsForm


def index(request):
    obj_list = ClinTemplate.objects.order_by('_template_id')
    return render_to_response('clintemplates_index.html', RequestContext( request, {'obj_list': obj_list, } ))

def detail(request, object_id):
    object = get_object_or_404(ClinTemplate, pk=object_id)
    check_permission(request.user, object.workgroup, 'resource', 'r')
    tView = request.GET.get('tView', 'form' if object.inf_model else 'docs')
    settingsform = TemplateSettingsForm(instance=object)
    if request.is_ajax():
        base_t = "clintemplates_detail_base_blank.html"
    else:
        base_t = "clintemplates_detail_base.html"

    t = 'clintemplates_detail_dataset.html' if tView == 'data' else 'clintemplates_detail.html'
    
    return render_to_response(t, RequestContext( request,
        {'base_template': base_t, 'clin_template': object, 'tView': tView, 'settingsform': settingsform }))

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

def new_template(request, group_slug):
    """docstring for new_template"""
    object = get_object_or_404(CTGroup, slug=group_slug)
    check_permission(request.user, object, 'resource', 'w')

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
                    rendered = render_to_string('clintemplates_new.xml', defaults )
                # print rendered
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
    check_permission(request.user, object.workgroup, 'resource', 'd')

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
                'title': _('Delete this %s?') % _(getattr(settings, 'RESOURCE_NAME', _('Clinical Template')))
            })
        )
    
@login_required
def edititem(request, object_id, view_id, item_id):
    object = get_object_or_404(ClinTemplate, pk=object_id)
    if not object.enable_editing:
        raise PermissionDenied()
    check_permission(request.user, object.workgroup, 'resource', 'w')
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
    check_permission(request.user, object.workgroup, 'resource', 'r')
    check_permission(request.user, object.workgroup, 'comment', 'r')
    tView = request.GET.get('tView', '0')
    # fix for mangled URL in email, eg tView=3D3
    if tView.startswith('3D'):
        tView = tView[2:]
    return render_to_response('clintemplates_detail.html', RequestContext( request, 
        {   'base_template': "clintemplates_detail_base.html", 'clin_template': object, 
            'comment_id': comment_id, 'tView': tView, 'settingsform': TemplateSettingsForm(instance=object)}))

@login_required
def addcomment(request, object_id, comment_id):
    object = get_object_or_404(ClinTemplate, pk=object_id)
    check_permission(request.user, object.workgroup, 'comment', 'w')
    
    if request.POST:
        tView = request.POST.get('tView', '0')
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
        tView = request.GET.get('tView', '0')
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
    check_permission(request.user, object.workgroup, 'comment', 'w')

    if request.method == 'POST':
        tView = request.POST.get('tView', '0')
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
        tView = request.GET.get('tView', '0')

    response = render_to_response('clintemplates_add_review.html',  
        RequestContext( request, { 'form': form, 'clin_template': object, 'tView': tView }) )
    return response

def get_node_metadata(request, object_id, node_id):
    object = get_object_or_404(ClinTemplate, pk=object_id)
    check_permission(request.user, object.workgroup, 'resource', 'r')

    # if request.is_ajax():
    node = object.get_item(node_id)
    return render_to_response('node_metadata.html', RequestContext( request,
        { 'elem': node, 'template': object }))
