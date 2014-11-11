from django.contrib import admin

from .models import Problem, Answer, Scale, Category


class ProblemAdmin(admin.ModelAdmin):
    list_display = (
        'item_number',
        'order',
        'question',
        'image_url',
    )
    list_filter = ('categories',)


admin.site.register(Scale)
admin.site.register(Category)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(Answer)
