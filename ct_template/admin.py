from django.contrib import admin
from django.forms import ModelForm, ValidationError
from ct_template.models import *


class ClinTemplateReviewInline(admin.TabularInline):
    model = ClinTemplateReview
    extra = 1


class ClinTemplateAdminForm(ModelForm):
    class Meta:
        model = ClinTemplate

    def clean(self):
        cleaned_data = self.cleaned_data
        temp = ClinTemplate(xmlmodel=cleaned_data.get("xmlmodel"))
        cleaned_data["_template_id"]= make_template_id(temp)
        return super(ClinTemplateAdminForm, self).clean()
    
class ClinTemplateAdmin(admin.ModelAdmin):
    form = ClinTemplateAdminForm
    ordering = ['_template_id']
    save_on_top = True
    # inlines = [ClinTemplateReviewInline]

admin.site.register(ClinTemplate, ClinTemplateAdmin)
admin.site.register(ClinTemplateReview)

