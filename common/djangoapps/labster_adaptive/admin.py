from django.contrib import admin

from .models import Problem, Answer, Scale, Station

admin.site.register(Scale)
admin.site.register(Station)
admin.site.register(Problem)
admin.site.register(Answer)
