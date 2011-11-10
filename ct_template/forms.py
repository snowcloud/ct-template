from django import forms
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from ct_template.models import ClinTemplate

class CTNewForm(forms.Form):
    title = forms.CharField(label=_('Title'))
    text = forms.CharField(label=_('Text'), widget=forms.Textarea(attrs={'class': 'item_big_text'}))
    
    def clean_title(self):
        t = slugify(self.cleaned_data['title'])
        if ClinTemplate.objects.filter(_template_id=t).exists():
            raise ValidationError(_('A resource with this name already exists.'))
        return self.cleaned_data['title']

class ItemForm(forms.Form):
    title = forms.CharField(label=_('Title'), widget=forms.HiddenInput())
    text = forms.CharField(label=_('Text'), widget=forms.Textarea(attrs={'class': 'item_big_text'}))

class ReviewForm(forms.Form):
    rating = forms.IntegerField()
    review = forms.CharField(widget=forms.Textarea(attrs={'rows': 20, 'cols': 50, 'class': 't_area'}))

    def clean_rating(self):
        try:
            if (self.cleaned_data.get('rating') < 1) or (self.cleaned_data.get('rating') > 5):
                raise ValidationError(u'Rating must be from 1-5.')
            return self.cleaned_data['rating']
        except AttributeError:
            return None

class TemplateSettingsForm(forms.ModelForm):
    """docstring for TemplateSettingsForm"""
    class Meta:
        model = ClinTemplate
        fields = ('tags', 'is_public', 'accept_comments', 'accept_reviews', 'enable_editing')

        # fields = ('name', 'note', 'tags', 'is_public', 'moderate_membership', 'moderated_message',
        #     'language', 'show_discussion', 'resource_comment_order', 'template', 'logo')

class NodeMetadataForm(forms.Form):
    name = forms.CharField(label=_('Name'))
    description = forms.CharField(label=_('Description'), widget=forms.Textarea(attrs={'class': 'item_big_text'}), required=False)
    datatype = forms.CharField(label=_('Datatype'), required=False)
    cardinality = forms.CharField(label=_('Cardinality'), required=False)
    coding = forms.CharField(label=_('Coding'), widget=forms.Textarea(attrs={'class': 'item_big_text'}), required=False)
