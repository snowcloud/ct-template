""" views for ct_template app

"""
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from ct_template.models import ClinTemplate, ClinTemplateReview
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import *

from ct_groups.decorators import check_permission

def index(request):
	obj_list = ClinTemplate.objects.order_by('_template_id')
	return render_to_response('clintemplates_index.html', RequestContext( request, {'obj_list': obj_list, } ))

def detail(request, object_id):
	object = get_object_or_404(ClinTemplate, pk=object_id)
	check_permission(request.user, object.workgroup, 'resource', 'r')
	tView = request.GET.get('tView', '0')
	
	if request.is_ajax():
		base_t = "clintemplates_detail_base_blank.html"
	else:
		base_t = "clintemplates_detail_base.html"
	t = 'clintemplates_detail.html'
	
	return render_to_response(t, RequestContext( request, {'base_template': base_t, 'clin_template': object, 'tView': tView }))

def showcomment(request, object_id, comment_id):
	object = get_object_or_404(ClinTemplate, pk=object_id)
	check_permission(request.user, object.workgroup, 'resource', 'r')
	check_permission(request.user, object.workgroup, 'comment', 'r')
	tView = request.GET.get('tView', '0')
	
	return render_to_response('clintemplates_detail.html', RequestContext( request, {'clin_template': object, 'comment_id': comment_id, 'tView': tView}))


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
		abs_comment_id = '%s_%s' % (object_id, comment_id)
		redirect_str = '%stemplates/%s/%s/?tView=%s#%s' % (settings.APP_BASE, template_id, abs_comment_id, tView, abs_comment_id)
		if request.POST['result'] == 'Cancel':
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

class ReviewForm(Form):
	rating = IntegerField()
	review = CharField(widget=Textarea(attrs={'rows': 20, 'cols': 50, 'class': 't_area'}))

	def clean_rating(self):
		try:
			if (self.cleaned_data.get('rating') < 1) or (self.cleaned_data.get('rating') > 5):
				raise ValidationError(u'Rating must be from 1-5.')
			return self.cleaned_data['rating']
		except AttributeError:
			return None

import datetime

@login_required
def addreview(request, object_id):
	object = get_object_or_404(ClinTemplate, pk=object_id)
	check_permission(request.user, object.workgroup, 'comment', 'w')

	if request.method == 'POST':
		tView = request.POST.get('tView', '0')
		redirect_str = '%stemplates/%s/?tView=%s' % (settings.APP_BASE, object.id, tView)
		if request.POST['result'] == 'Cancel':
			return HttpResponseRedirect(redirect_str)
		else:
			form = ReviewForm(request.POST)
			if form.is_valid():
				r = ClinTemplateReview()
				r.rating = str(form.clean()['rating'])
				r.review = str(form.clean()['review'])
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
