from django.contrib import admin

from labster_search.models import LabKeyword


class LabKeywordAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'lab', 'keyword', 'keyword_type', 'source', 'frequency')
    list_filter = ('lab', 'keyword_type', 'source')
    search_fields = ('keyword',)


admin.site.register(LabKeyword, LabKeywordAdmin)
