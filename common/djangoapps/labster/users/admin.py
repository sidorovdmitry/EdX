from django.contrib import admin

from labster.users.forms import LabsterUserForm


def make_active(modeladmin, request, queryset):
    queryset.update(is_active= True)
make_active.short_description = "Set active"

def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active= False)
make_inactive.short_description = "Set inactive"


class LabsterUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'user_id', 'username', 'user_type_display', 'is_active', 'ip_address')
    search_fields = ('user__email', 'user__username',)
    list_filter = ('user__is_active', 'user_type', 'is_new')
    raw_id_fields = ('user',)
    actions = (make_active, make_inactive)
    fieldsets = (
        (None, {'fields': (
            # 'user',
            'email',
            'password',
            'user_is_active',
        )}),
        (None, {
            'fields': (
                'name',
                'is_active',
                'is_email_active',
                'gender',
                'level_of_education',
            )
        }),
        (None, {
            'fields': (
                'user_type',
                'organization_name',
                'user_school_level',
                'phone_number',
                'date_of_birth',
                'language',
                'nationality',
                'unique_id',
            )
        }),
    )
    form = LabsterUserForm

    def email(self, obj):
        return obj.user.email

    def user_id(self, obj):
        return obj.user.id

    def username(self, obj):
        return obj.user.username

    def user_type_display(self, obj):
        return obj.get_user_type_display()
