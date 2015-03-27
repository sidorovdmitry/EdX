from django.contrib import admin

from labster_frontend.models import DemoCourse


class DemoCourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'lab_name', 'slug', 'is_active',)

    def lab_name(self, obj):
        return obj.lab.name if obj.lab else ""


admin.site.register(DemoCourse, DemoCourseAdmin)
