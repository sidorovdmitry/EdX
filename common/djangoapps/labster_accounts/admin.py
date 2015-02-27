from django.contrib import admin

from labster_accounts.models import Organization


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('label', 'created_at')
    search_fields = ('name',)


admin.site.register(Organization, OrganizationAdmin)
