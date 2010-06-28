from django.forms import *
from django.utils.translation import ugettext_lazy as _


class CTNewForm(Form):
    title = CharField(label=_('Title'))
    text = CharField(label=_('Text'), widget=Textarea(attrs={'class': 'item_big_text'}))

class ItemForm(Form):
    title = CharField(label=_('Title'), widget=HiddenInput())
    text = CharField(label=_('Text'), widget=Textarea(attrs={'class': 'item_big_text'}))

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

