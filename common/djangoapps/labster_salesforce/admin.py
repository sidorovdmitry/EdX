from django.contrib import admin

from labster_salesforce.models import Lead, Account, Contact


class LeadAdmin(admin.ModelAdmin):
    list_display = ('lead_id', 'user')
    search_fields = ('user__email', 'user__username')


class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_id', 'organization')
    search_fields = ('organization__name',)


class ContactAdmin(admin.ModelAdmin):
    list_display = ('contact_id', 'user')
    search_fields = ('user__email', 'user__username')


admin.site.register(Lead, LeadAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Contact, ContactAdmin)
