from django.contrib import admin
from ct_tools.ct_template.models import *


class ClinTemplateReviewInline(admin.TabularInline):
    model = ClinTemplateReview
    extra = 1
    
class ClinTemplateAdmin(admin.ModelAdmin):
    # change_list_template = 'smuggler/change_list.html'
    ordering = ['_template_id']
    save_on_top = True
    # inlines = [ClinTemplateReviewInline]

admin.site.register(ClinTemplate, ClinTemplateAdmin)
admin.site.register(ClinTemplateReview)

