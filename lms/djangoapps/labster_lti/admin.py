from django.contrib import admin

from labster_lti.models import LTIUser


class LTIUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'external_user_id', 'provider', 'created_at')
    list_filter = ('provider',)


admin.site.register(LTIUser, LTIUserAdmin)
