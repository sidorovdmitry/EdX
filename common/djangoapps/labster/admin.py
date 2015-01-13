import requests

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from labster.models import (
    LanguageLab, Lab, ErrorInfo, DeviceInfo, UserSave, Token, LabProxy,
    UnityLog, UserAnswer, LabsterUserLicense, ProblemProxy,
    UnityPlatformLog, QuizBlock, Problem, Answer, AdaptiveProblem,
    LabProxyData, UserAttempt, LabsterUser, LabsterCourseLicense)
from labster.utils import get_engine_xml_url, get_engine_file_url, get_quiz_block_file_url


S3_BASE_URL = settings.LABSTER_S3_BASE_URL
ENGINE_S3_PATH = '{}unity/ModularLab/{}'
QUIZ_BLOCK_S3_PATH = '{}uploads/{}'
HTML_LINK = """<a href="{}">{}</a>"""


class BaseAdmin(admin.ModelAdmin):
    exclude = ('created_at', 'modified_at')


class LabAdminForm(forms.ModelForm):

    class Meta:
        model = Lab
        fields = (
            'name', 'description',
            'engine_xml',
            'engine_file',
            'quiz_block_file',
            'xml_url_prefix',
            'languages',
            'use_quiz_blocks', 'is_active', 'demo_course_id',
            'verified_only')

    def clean(self):
        cleaned_data = super(LabAdminForm, self).clean()
        xml_url_prefix = cleaned_data['xml_url_prefix']
        engine_xml = self.cleaned_data['engine_xml']
        quiz_block_file = self.cleaned_data['quiz_block_file']

        # engine xml
        engine_xml_url = get_engine_xml_url(xml_url_prefix, engine_xml)
        response = requests.head(engine_xml_url)
        if response.status_code != 200:
            self._errors['engine_xml'] = self.error_class(['No engine xml found'])
            del cleaned_data['engine_xml']

        # quiz block file
        quiz_block_file_url = get_quiz_block_file_url(quiz_block_file)
        response = requests.head(quiz_block_file_url)
        if response.status_code != 200:
            self._errors['quiz_block_file'] = self.error_class(['No quiz block file found'])
            del cleaned_data['quiz_block_file']

        return cleaned_data


class LabAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'engine_xml_link', 'engine_file_link', 'quiz_block_file_link',
        'use_quiz_blocks', 'demo_course_id', 'xml_url_prefix', 'is_active')
    # fields = (
    #     'name', 'description', 'engine_xml', 'languages', 'engine_file',
    #     'quiz_block_file', 'use_quiz_blocks', 'is_active', 'demo_course_id',
    #     'verified_only')
    filter_horizontal = ('languages',)
    list_filter = ('is_active', 'engine_file')
    form = LabAdminForm

    def queryset(self, request):
        return Lab.all_objects.all()

    def engine_xml_link(self, obj):
        return HTML_LINK.format(obj.engine_xml_url, obj.engine_xml)
    engine_xml_link.allow_tags = True
    engine_xml_link.short_description = "Engine XML"

    def engine_file_link(self, obj):
        return HTML_LINK.format(obj.engine_file_url, obj.engine_file)
    engine_file_link.allow_tags = True
    engine_file_link.short_description = "Engine file"

    def quiz_block_file_link(self, obj):
        return HTML_LINK.format(obj.quiz_block_file_url, obj.quiz_block_file)
    quiz_block_file_link.allow_tags = True
    quiz_block_file_link.short_description = "Quiz block file"


class QuizBlockAdmin(BaseAdmin):
    list_display = ('element_id', 'lab', 'order')
    list_filter = ('lab',)
    search_fields = ('element_id',)

    def queryset(self, request):
        return QuizBlock.objects.filter(is_active=True)


class ProblemAdmin(BaseAdmin):
    list_display = ('element_id', 'quiz_block', 'order', 'sentence')
    search_fields = ('element_id', 'quiz_block__element_id')
    raw_id_fields = ('quiz_block',)
    list_filter = ('quiz_block__lab',)

    def queryset(self, request):
        return Problem.objects.filter(is_active=True)


class AdaptiveProblemAdmin(ProblemAdmin):
    list_display = ('element_id', 'quiz_block', 'answer_type', 'number_of_destractors',
                    'time', 'sd_time', 'discrimination', 'guessing', 'image_url')
    list_filter = ('quiz_block__lab',)

    def queryset(self, request):
        return AdaptiveProblem.objects.all()


class AnswerAdmin(BaseAdmin):
    list_display = ('text', 'problem', 'order', 'is_correct')
    list_filter = ('problem__quiz_block__lab',)
    raw_id_fields = ('problem',)

    def queryset(self, request):
        return Answer.objects.filter(is_active=True)


class LabProxyAdmin(BaseAdmin):
    list_display = ('id', 'course_from_location', 'lab', 'location', 'is_active', 'created_at')
    list_filter = ('is_active',)


class LabProxyDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'data_file_link', 'lab_proxy_id', 'created_at')
    list_filter = ('lab_proxy',)

    def lab_proxy_id(self, obj):
        return obj.lab_proxy.id

    def data_file_link(self, obj):
        return HTML_LINK.format(obj.data_file.url, obj.data_file_name)
    data_file_link.allow_tags = True


class ProblemProxyAdmin(admin.ModelAdmin):
    list_display = ('id', 'lab_proxy_id', 'problem', 'is_active')
    list_filter = ('is_active',)
    raw_id_fields = ('lab_proxy', 'problem')

    def lab_proxy_id(self, obj):
        return obj.lab_proxy.id


class UserSaveAdmin(BaseAdmin):
    list_display = ('user', 'lab', 'location', 'has_file', 'modified_at')

    def lab(self, obj):
        return obj.lab_proxy.lab.name

    def location(self, obj):
        return obj.lab_proxy.location

    def has_file(self, obj):
        return obj.save_file is not None


class ErrorInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'lab', 'browser', 'os', 'message', 'created_at')

    def lab(self, obj):
        return obj.lab_proxy.lab.name


class DeviceInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'lab', 'device_id', 'frame_rate', 'machine_type', 'os',
                    'ram', 'processor', 'cores', 'gpu', 'memory', 'fill_rate',
                    'shader_level', 'quality', 'misc')

    def lab(self, obj):
        return obj.lab_proxy.lab.name


class TokenAdmin(admin.ModelAdmin):
    exclude = ('key', 'created_at')
    list_display = ('name', 'key', 'created_at')


class UnityLogAdmin(admin.ModelAdmin):
    list_filter = ('log_type',)
    list_display = ('user', 'lab_proxy', 'log_type', 'created_at')


class UnityPlatformLogAdmin(admin.ModelAdmin):
    list_filter = ('tag',)
    list_display = ('user', 'lab', 'lab_proxy_id', 'created_at', 'tag', 'message')
    search_fields = ('user__email', 'user__profile__name', 'lab_proxy__lab__name', 'message')

    def lab_proxy_id(self, obj):
        return obj.lab_proxy.id

    def lab(self, obj):
        return obj.lab_proxy.lab.name


class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'lab', 'created_at', 'question', 'quiz_id',
                    'answer_string', 'correct_answer', 'is_correct', 'attempt_id')
    raw_id_fields = ('problem',)
    list_filter = ('is_correct',)
    search_fields = ('quiz_id',)

    def lab(self, obj):
        return obj.lab_proxy.lab.name

    def question(self, obj):
        return obj.problem.sentence

    def attempt_id(self, obj):
        if not obj.attempt:
            return ''
        return obj.attempt.id


class LabsterUserLicenseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'email', 'created_at', 'expired_at')
    search_fields = ('email', 'course_id')


class UserAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'lab_proxy_id', 'lab', 'user', 'created_at',
                    'is_completed', 'completed_at')
    list_filter = ('is_completed', 'lab_proxy')

    def lab(self, obj):
        return obj.lab_proxy.lab.name

    def lab_proxy_id(self, obj):
        return obj.lab_proxy.id


class LabsterUserAdmin(admin.ModelAdmin):
    pass


class LabsterCourseLicenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_id', 'course_id', 'license_id')
    search_fields = ('user__id', 'course_id')

    def user_id(self, obj):
        return obj.user.id


admin.site.register(LabsterUser, LabsterUserAdmin)
admin.site.register(LanguageLab)
# admin.site.register(ErrorInfo, ErrorInfoAdmin)
# admin.site.register(DeviceInfo, DeviceInfoAdmin)
admin.site.register(UserSave, UserSaveAdmin)
admin.site.register(UserAnswer, UserAnswerAdmin)
admin.site.register(UserAttempt, UserAttemptAdmin)
admin.site.register(Token, TokenAdmin)

admin.site.register(Lab, LabAdmin)
admin.site.register(QuizBlock, QuizBlockAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(AdaptiveProblem, AdaptiveProblemAdmin)
admin.site.register(Answer, AnswerAdmin)

admin.site.register(LabProxy, LabProxyAdmin)
admin.site.register(ProblemProxy, ProblemProxyAdmin)
admin.site.register(LabProxyData, LabProxyDataAdmin)

admin.site.register(UnityLog, UnityLogAdmin)
admin.site.register(UnityPlatformLog, UnityPlatformLogAdmin)
admin.site.register(LabsterUserLicense, LabsterUserLicenseAdmin)
admin.site.register(LabsterCourseLicense, LabsterCourseLicenseAdmin)


# remove defaul UserAdmin and replace it
admin.site.unregister(User)


class CustomUserAdmin(UserAdmin):

    def set_active(self, request, queryset):
        queryset.update(is_active=True)
    set_active.short_descripion = "Set users active."

    def set_inactive(self, request, queryset):
        queryset.update(is_active=False)
    set_inactive.short_descripion = "Set users inactive."

    actions = UserAdmin.actions + [set_active, set_inactive]


admin.site.register(User, CustomUserAdmin)
