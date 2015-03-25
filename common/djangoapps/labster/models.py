import binascii
import calendar
import json
import os
import re
import uuid

from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count, Q
from django.db.models.signals import pre_save, post_save
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_noop

from django_countries.fields import CountryField

from xmodule_django.models import CourseKeyField, LocationKeyField

from labster_accounts.models import Organization
from labster.utils import get_engine_xml_url, get_engine_file_url, get_quiz_block_file_url
from labster_salesforce.models import Lead


PLATFORM_NAME = 'platform'
URL_PREFIX = getattr(settings, 'LABSTER_UNITY_URL_PREFIX', '')
ENGINE_FILE = 'labster.unity3d'


class LabsterUser(models.Model):
    user = models.OneToOneField(User, related_name='labster_user')

    USER_TYPE_STUDENT = 1
    USER_TYPE_TEACHER = 2
    USER_TYPE_CHOICES = (
        (USER_TYPE_STUDENT, ugettext_noop('Student')),
        (USER_TYPE_TEACHER, ugettext_noop('Teacher')),
    )
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, default="")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    organization_name = models.CharField(max_length=255, blank=True, default="")
    organization = models.ForeignKey(Organization, blank=True, null=True)

    USER_HIGH_SCHOOL = 1
    USER_COLLEGE = 2
    USER_UNIVERSITY = 3
    USER_EDUCATION_MANAGER = 4
    USER_DEAN = 5
    USER_OTHER = 10
    USER_SCHOOL_LEVEL_CHOICES = (
        (USER_HIGH_SCHOOL, ugettext_noop('High School Teacher')),
        (USER_COLLEGE, ugettext_noop('College Teacher')),
        (USER_UNIVERSITY, ugettext_noop('University Teacher/Professor')),
        (USER_EDUCATION_MANAGER, ugettext_noop('Education Manager')),
        (USER_DEAN, ugettext_noop('Dean')),
        (USER_OTHER, ugettext_noop('Other')),
    )
    user_school_level = models.IntegerField(choices=USER_SCHOOL_LEVEL_CHOICES, blank=True, null=True)

    # labster verified account
    language = models.CharField(blank=True, max_length=255, db_index=True)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = CountryField(blank=True, null=True)
    unique_id = models.CharField(max_length=100, blank=True, db_index=True)

    is_new = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_email_active = models.BooleanField(default=False)
    email_activation_key = models.CharField(
        max_length=32, db_index=True, blank=True, default="")

    def __unicode__(self):
        return unicode(self.user)

    @property
    def token_key(self):
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=self.user)
        return token.key

    @property
    def is_labster_verified(self):
        reqs = [self.language, self.date_of_birth, self.nationality, self.unique_id]
        return all(reqs)

    @property
    def is_teacher(self):
        return self.user_type == self.USER_TYPE_TEACHER

    @property
    def is_student(self):
        return self.user_type == self.USER_TYPE_STUDENT

    @property
    def is_high_school(self):
        return self.user_school_level == self.USER_HIGH_SCHOOL

    @property
    def is_university(self):
        universities = [
            None,
            self.USER_COLLEGE,
            self.USER_UNIVERSITY,
            self.USER_EDUCATION_MANAGER,
            self.USER_DEAN,
            self.USER_OTHER,
        ]
        return self.user_school_level in universities

    @property
    def is_lead_synced(self):
        """
        default to True
        if it's False, it'll create Lead object in labster_salesforce
        """
        if self.is_teacher:
            return Lead.objects.filter(user=self.user).exists()
        return True

    def save(self, *args, **kwargs):
        if not self.is_email_active and not self.email_activation_key:
            self.email_activation_key = uuid.uuid4().hex
        return super(LabsterUser, self).save(*args, **kwargs)


def create_labster_user(sender, instance, created, **kwargs):
    if created:
        LabsterUser.objects.get_or_create(user=instance)
post_save.connect(create_labster_user, sender=User)


class NutshellUser(models.Model):
    user = models.OneToOneField(User)

    # nutshell stuff
    account_id = models.CharField(max_length=100, db_index=True)
    contact_id = models.CharField(max_length=100, db_index=True)
    lead_id = models.CharField(max_length=100, db_index=True)


class Token(models.Model):
    name = models.CharField(max_length=100, unique=True)
    key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    @classmethod
    def get_for_platform(self):
        obj, _ = self.objects.get_or_create(name=PLATFORM_NAME)
        return obj

    def __unicode__(self):
        return self.name

    def for_header(self):
        return "Token {}".format(self.key)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super(Token, self).save(*args, **kwargs)


class ActiveManager(models.Manager):
    def get_query_set(self):
        qs = super(ActiveManager, self).get_query_set()
        return qs.filter(is_active=True)


class Lab(models.Model):
    """
    Master Lab
    """
    name = models.CharField(max_length=64)
    description = models.TextField(default='')
    engine_xml = models.CharField(max_length=128, default="")
    engine_file = models.CharField(max_length=128, blank=True, default=ENGINE_FILE)
    quiz_block_file = models.CharField(max_length=128, default="")
    quiz_block_last_updated = models.DateTimeField(blank=True, null=True)

    demo_course_id = CourseKeyField(max_length=255, db_index=True, blank=True,
                                    null=True)

    use_quiz_blocks = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    verified_only = models.BooleanField(default=False)

    xml_url_prefix = models.CharField(
        max_length=255,
        default=URL_PREFIX)

    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    all_objects = models.Manager()
    objects = ActiveManager()

    @classmethod
    def fetch_with_lab_proxies(self):
        labs = Lab.objects.order_by('name')\
            .annotate(labproxy_count=Count('labproxy'))
        return labs

    @classmethod
    def update_quiz_block_last_updated(self, lab_id):
        Lab.objects.filter(id=lab_id).update(quiz_block_last_updated=timezone.now())

    def __unicode__(self):
        return self.name

    @property
    def slug(self):
        """
        converts `Engine_CrimeScene_OVR.xml`
        to `CrimeScene_OVR`
        """

        try:
            return self.engine_xml.split('Engine_')[1].split('.xml')[0]
        except:
            return ''

    @property
    def studio_detail_url(self):
        return "/labster/labs/{}/".format(self.id)

    @property
    def new_quiz_block_url(self):
        return reverse('labster_create_quiz_block', args=[self.id])

    @property
    def engine_xml_url(self):
        return get_engine_xml_url(self.xml_url_prefix, self.engine_xml)

    @property
    def engine_file_url(self):
        return get_engine_file_url(self.xml_url_prefix, self.engine_file)

    @property
    def quiz_block_file_url(self):
        return get_quiz_block_file_url(self.quiz_block_file)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'template_location': '',
        }

    def get_quizblocks(self):
        return self.quizblocklab_set.all()


class QuizBlock(models.Model):
    """
    Master QuizBlock
    """
    lab = models.ForeignKey(Lab)
    element_id = models.CharField(max_length=100, db_index=True)

    time_limit = models.IntegerField(blank=True, null=True)
    order = models.IntegerField(default=0)
    can_skip = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('lab', 'element_id')
        ordering = ('order', 'created_at')

    def __unicode__(self):
        return "{}: {}".format(self.lab.name, self.element_id)


class Scale(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name


class Problem(models.Model):
    """
    Master Problem
    """
    quiz_block = models.ForeignKey(QuizBlock)
    element_id = models.CharField(max_length=100, db_index=True)

    sentence = models.TextField()
    correct_message = models.TextField(default="", blank=True)
    wrong_message = models.TextField(default="", blank=True)
    hashed_sentence = models.CharField(max_length=50, default="", db_index=True)

    no_score = models.BooleanField(default=False)
    max_attempts = models.IntegerField(blank=True, null=True)
    randomize_option_order = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    current_conv_popup_id = models.CharField(max_length=100, default="", blank=True)
    image_id = models.CharField(max_length=100, default="", blank=True)
    read_more_url = models.CharField(max_length=100, default="", blank=True)
    is_explorable = models.BooleanField(default=False)
    quiz_group = models.CharField(max_length=100, default="", blank=True)

    is_adaptive = models.BooleanField(default=False)

    # adaptive fields
    ANSWER_TYPE_CHOICES = (
        (1, 'dichotomous'),
        (2, '3 response options'),
        (3, '4 response options'),
        # (4, '5 response options'),
        # (5, '6 response options'),
    )
    answer_type = models.IntegerField(choices=ANSWER_TYPE_CHOICES, blank=True, null=True)
    number_of_destractors = models.IntegerField(blank=True, null=True)
    content = models.TextField(default="", blank=True)
    feedback = models.TextField(default="", blank=True)
    time = models.FloatField(blank=True, null=True)
    sd_time = models.FloatField(blank=True, null=True)
    discrimination = models.IntegerField(blank=True, null=True)
    guessing = models.FloatField(blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, default="")
    scales = models.ManyToManyField(Scale, blank=True)
    categories = models.ManyToManyField(Category, blank=True)
    direction_for_scoring = models.CharField(max_length=50, blank=True, default="")
    # end of adaptive fields

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('quiz_block', 'element_id')
        ordering = ('order', 'created_at')

    def __unicode__(self):
        return "{}: {}".format(self.quiz_block, self.element_id)

    @classmethod
    def get_by_lab(cls, lab):
        return cls.objects.filter(quiz_block__lab=lab)

    @property
    def correct_answers(self):
        try:
            return Answer.objects.filter(is_active=True, problem=self, is_correct=True)
        except Answer.DoesNotExist:
            return None

    @property
    def correct_answer_texts(self):
        if self.correct_answers:
            return [each.text.strip() for each in self.correct_answers]
        return ""


class AdaptiveProblemManager(models.Manager):
    def get_query_set(self):
        qs = super(AdaptiveProblemManager, self).get_query_set()
        qs = qs.filter(is_adaptive=True)
        return qs


class AdaptiveProblem(Problem):
    objects = AdaptiveProblemManager()

    class Meta:
        proxy = True


class Answer(models.Model):
    """
    Master Answer
    """

    problem = models.ForeignKey(Problem)
    text = models.TextField()
    hashed_text = models.CharField(max_length=50, db_index=True)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    # for adaptive
    score = models.IntegerField(blank=True, null=True)
    difficulty = models.IntegerField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('problem', 'hashed_text')
        ordering = ('order', 'created_at')

    def __unicode__(self):
        return "{}: {} ({})".format(
            self.problem,
            self.text,
            "correct" if self.is_correct else "incorrect")


class LabProxy(models.Model):
    """
    Stores connection between subsection and lab
    """

    lab = models.ForeignKey(Lab, blank=True, null=True)
    location = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    all_objects = models.Manager()
    objects = ActiveManager()

    class Meta:
        verbose_name_plural = 'Lab proxies'

    def __unicode__(self):
        return "{}: {}".format(self.id, self.lab.name)

    @property
    def course_from_location(self):
        paths = self.location.split('/')
        return '/'.join([paths[2], paths[3]])

    @property
    def latest_data(self):
        try:
            return LabProxyData.objects.filter(lab_proxy=self).latest('created_at')
        except LabProxyData.DoesNotExist:
            return None


class LabProxyData(models.Model):
    lab_proxy = models.ForeignKey(LabProxy)
    data_file = models.FileField(upload_to='edx/labster/lab_proxy/data')
    score_file = models.FileField(upload_to='edx/labster/lab_proxy/score', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    @property
    def data_file_name(self):
        name = self.data_file.name.split('/')[-1]
        return name


class UserSave(models.Model):
    """
    SavePoint need to be linked to LabProxy instead of Lab

    The way we designed the system, many courses could use same lab,
    with different set of questions.
    """
    lab_proxy = models.ForeignKey(LabProxy)
    user = models.ForeignKey(User)
    save_file = models.FileField(blank=True, null=True, upload_to='edx/labster/lab/save')
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    # these will be deleted
    play_count = models.IntegerField(default=0)
    is_finished = models.BooleanField(default=False)

    class Meta:
        unique_together = ('lab_proxy', 'user')

    def get_new_save_file_name(self):
        timestamp = calendar.timegm(datetime.utcnow().utctimetuple())
        file_name = "{}_{}_{}.zip".format(timestamp, self.lab_proxy_id, self.user_id)
        return file_name


class UserAttemptManager(models.Manager):
    def latest_for_user(self, lab_proxy, user=None, user_id=None):
        if user is None:
            user = User.objects.get(id=user_id)
        try:
            return self.get_query_set().filter(
                is_finished=False, lab_proxy=lab_proxy, user=user).latest('created_at')
        except self.model.DoesNotExist:
            return None


class UserAttempt(models.Model):
    lab_proxy = models.ForeignKey(LabProxy)
    user = models.ForeignKey(User)

    problems = models.ManyToManyField(
        Problem, blank=True,
        help_text="Problems used for this attempt. Empty means any currently active problems.")
    score = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    # user is finished with this attempt (could be completed or starting new one)
    is_finished = models.BooleanField(default=False)
    finished_at = models.DateTimeField(blank=True, null=True)

    # the lab is completed
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    objects = UserAttemptManager()

    class Meta:
        ordering = ('-created_at',)

    @property
    def play(self):
        return 0

    @cached_property
    def problems_count(self):
        return Problem.objects.filter(
            is_active=True,
            no_score=False,
            quiz_block__lab=self.lab_proxy.lab,
        ).count()

    @cached_property
    def answers_count(self):
        user_answers = UserAnswer.objects.filter(
            attempt=self,
            problem__is_active=True,
            problem__no_score=False,
        )

        problem_ids = list(user_answers.values_list('problem__id', flat=True))
        problem_ids = list(set(problem_ids))
        return len(problem_ids)

    @cached_property
    def correct_answers_count(self):
        user_answers = UserAnswer.objects.filter(
            attempt=self,
            is_correct=True,
            problem__is_active=True,
            problem__no_score=False,
        )

        problem_ids = list(user_answers.values_list('problem__id', flat=True))
        problem_ids = list(set(problem_ids))
        return len(problem_ids)

    @cached_property
    def progress_in_percent(self):
        return 100 * self.answers_count / self.problems_count

    def get_score(self):
        user_answers = UserAnswer.objects.filter(
            attempt=self,
            is_correct=True,
            problem__is_active=True,
            problem__no_score=False,
        ).order_by('-created_at')

        score = 0
        picked = []

        for user_answer in user_answers:
            if not user_answer.problem.id in picked:
                picked.append(user_answer.problem.id)
                score += user_answer.score

        score = 10 * score / self.problems_count
        return score

    def check_completed(self):
        problem_quiz_ids = Problem.objects.filter(
            is_active=True,
            quiz_block__lab=self.lab_proxy.lab).values_list('element_id', flat=True)

        answer_quiz_ids = UserAnswer.objects.filter(
            attempt=self,
            problem__is_active=True).values_list('quiz_id', flat=True)

        problem_quiz_ids = list(problem_quiz_ids)
        answer_quiz_ids = list(answer_quiz_ids)

        for quiz_id in answer_quiz_ids:
            if quiz_id not in problem_quiz_ids:
                return False

        for quiz_id in problem_quiz_ids:
            if quiz_id not in answer_quiz_ids:
                return False

        return True

    def mark_finished(self):
        self.is_finished = True
        self.finished_at = timezone.now()
        self.save()

    def get_total_play_count(self):
        return UserAttempt.objects.filter(
            user=self.user, lab_proxy=self.lab_proxy).count()

    def save(self, *args, **kwargs):
        if not self.is_completed:
            self.is_completed = self.check_completed()

        return super(UserAttempt, self).save(*args, **kwargs)


class ErrorInfo(models.Model):
    user = models.ForeignKey(User)
    lab_proxy = models.ForeignKey(LabProxy)
    browser = models.CharField(max_length=64, blank=True, default="")
    os = models.CharField(max_length=32, blank=True, default="")
    user_agent = models.CharField(max_length=200, blank=True, default="")
    message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)


class DeviceInfo(models.Model):
    user = models.ForeignKey(User)
    lab_proxy = models.ForeignKey(LabProxy)

    cores = models.CharField(default="", max_length=128, blank=True)
    device_id = models.CharField(default="", max_length=128, blank=True)
    fill_rate = models.CharField(default="", max_length=128, blank=True)
    frame_rate = models.CharField(default="", max_length=128, blank=True)
    gpu = models.CharField(default="", max_length=128, blank=True)
    machine_type = models.CharField(default="", max_length=128, blank=True)
    memory = models.CharField(default="", max_length=128, blank=True)
    misc = models.TextField(default="", blank=True)
    os = models.CharField(default="", max_length=32, blank=True)
    processor = models.CharField(default="", max_length=128, blank=True)
    quality = models.CharField(default="", max_length=128, blank=True)
    ram = models.CharField(default="", max_length=32, blank=True)
    shader_level = models.CharField(default="", max_length=128, blank=True)

    created_at = models.DateTimeField(default=timezone.now)


class UnityLogManager(models.Manager):

    def get_query_set(self):
        qs = super(UnityLogManager, self).get_query_set()
        return qs.exclude(log_type='UNITY_LOG')


def separate_tag_from_message(message):
    tag = ''
    search = re.search(r'^\[(\w+)\] (.+)', message)
    if search:
        tag, message = search.groups()
    return tag, message


class UnityLog(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    lab_proxy = models.ForeignKey(LabProxy, blank=True, null=True)

    log_type = models.CharField(max_length=100, db_index=True)
    url = models.CharField(max_length=255, default='')
    request_method = models.CharField(max_length=10, blank=True, default='')
    message = models.TextField(help_text="JSON representation of data")
    tag = models.CharField(max_length=50, default="INFO", db_index=True)

    created_at = models.DateTimeField(default=timezone.now)
    objects = UnityLogManager()

    def get_message(self):
        if self.message:
            return json.loads(self.message)
        return None

    def set_message(self, message):
        self.message = json.dumps(message)

    def save(self, *args, **kwargs):
        self.log_type = self.log_type.strip().upper()
        return super(UnityLog, self).save(*args, **kwargs)

    @classmethod
    def new(self, user, lab_proxy, log_type, message, url='', request_method=''):
        message = json.dumps(message)
        return self.objects.create(
            user=user, lab_proxy=lab_proxy,
            log_type=log_type, message=message, url=url, request_method=request_method)

    @classmethod
    def new_unity_log(self, user, lab_proxy, message, url='', request_method=''):
        tag, message = separate_tag_from_message(message)
        return self.objects.create(
            user=user,
            lab_proxy=lab_proxy,
            log_type='UNITY_LOG',
            message=message,
            tag=tag,
            url=url,
            request_method=request_method)


class UnityPlatformLogManager(models.Manager):

    def get_query_set(self):
        qs = super(UnityPlatformLogManager, self).get_query_set()
        return qs.filter(log_type='UNITY_LOG')


class UnityPlatformLog(UnityLog):
    objects = UnityPlatformLogManager()
    class Meta:
        proxy = True


class ProblemProxy(models.Model):
    """
    Model to store connection between quiz and the location
    """

    lab_proxy = models.ForeignKey(LabProxy)
    problem = models.ForeignKey(Problem, blank=True, null=True)
    location = LocationKeyField(max_length=255, db_index=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    # FIXME: delete
    quiz_id = models.CharField(max_length=100, db_index=True)
    question = models.CharField(max_length=100, db_index=True, help_text='Question in md5')
    question_text = models.TextField(default='')
    location = models.CharField(max_length=200)
    correct_answer = models.TextField()

    def __unicode__(self):
        return str(self.id)


class UserAnswer(models.Model):
    user = models.ForeignKey(User)
    attempt = models.ForeignKey(UserAttempt, blank=True, null=True)

    lab_proxy = models.ForeignKey(LabProxy, blank=True, null=True)
    problem = models.ForeignKey(Problem, blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    quiz_id = models.CharField(max_length=100, blank=True, default='')
    question = models.TextField(default='')
    answer_string = models.TextField(default='')
    correct_answer = models.TextField(default='')
    is_correct = models.BooleanField(default=True)

    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    completion_time = models.FloatField(blank=True, null=True)

    attempt_count = models.IntegerField(blank=True, null=True)
    play_count = models.IntegerField(blank=True, null=True)

    score = models.IntegerField(blank=True, null=True)
    answer_index = models.IntegerField(default=0)

    is_view_theory_clicked = models.BooleanField(default=False)

    # FIXME: delete
    problem_proxy = models.ForeignKey(ProblemProxy, blank=True, null=True)


# FIXME: unused
def fetch_labs_as_json():
    labs = Lab.objects.order_by('name')
    labs_json = [lab.to_json() for lab in labs]
    return labs_json


def get_or_create_lab_proxy(location, lab=None):
    location = location.strip()
    try:
        lab_proxy = LabProxy.objects.get(location=location)
        created = False
    except LabProxy.DoesNotExist:
        lab_proxy = LabProxy(location=location)
        created = True

    modified = all([lab is not None, lab_proxy.lab is not lab])
    if modified:
        lab_proxy.lab = lab

    if created or modified:
        lab_proxy.save()

    return lab_proxy


def fetch_lab_data(sender, instance, created, **kwargs):
    from labster.masters import fetch_quizblocks
    fetch_quizblocks(instance)
post_save.connect(fetch_lab_data, sender=Lab)


def update_modified_at(sender, instance, **kwargs):
    instance.modified_at = timezone.now()
pre_save.connect(update_modified_at, sender=Lab)
pre_save.connect(update_modified_at, sender=QuizBlock)
pre_save.connect(update_modified_at, sender=Problem)
pre_save.connect(update_modified_at, sender=Answer)
pre_save.connect(update_modified_at, sender=LabProxy)
pre_save.connect(update_modified_at, sender=UserSave)
pre_save.connect(update_modified_at, sender=UserAttempt)
pre_save.connect(update_modified_at, sender=Lab)


class LabsterUserLicense(models.Model):
    """
    Tracks user's licenses against course
    """
    course_id = CourseKeyField(max_length=255, db_index=True)
    email = models.EmailField(max_length=255)
    voucher_code = models.CharField(max_length=50, blank=True, default="")

    created_at = models.DateTimeField(default=timezone.now)
    expired_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('course_id', 'email')

    @classmethod
    def course_licenses_count(cls, course_id):
        now = timezone.now()
        no_expired = {'course_id': course_id, 'expired_at': None}
        expired = {'course_id': course_id, 'expired_at__gte': now}
        return cls.objects.filter(Q(**no_expired) | Q(**expired)).count()

    @classmethod
    def get_for_course(cls, course_id, as_json=False):
        objs = cls.objects.filter(course_id=course_id)
        if as_json:
            return [obj.to_json() for obj in objs]
        return objs

    def __unicode__(self):
        return "{} - {}".format(self.course_id, self.email)

    @property
    def is_expired(self):
        return self.expired_at and timezone.now() > self.expired_at

    def renew_to(self, expired_at):
        self.expired_at = expired_at
        self.save()

    def to_json(self):
        return {
            'course_id': self.course_id.to_deprecated_string(),
            'email': self.email,
        }


class LabsterCourseLicense(models.Model):
    user = models.ForeignKey(User)  # the teacher
    course_id = CourseKeyField(max_length=255, db_index=True)
    license_id = models.IntegerField(db_index=True)

    class Meta:
        unique_together = ('course_id', 'license_id')


def get_user_attempts_from_lab_proxy(lab_proxy):
    user_attempts = UserAttempt.objects.filter(lab_proxy=lab_proxy)
    user_attempts = user_attempts.exclude(user__email__endswith='labster.com')
    user_attempts = user_attempts.exclude(user__email__endswith='liv.it')
    user_attempts = user_attempts.exclude(user__email='mitsurudy@gmail.com')
    return user_attempts


# class DemoCourse(models.Model):
#     course_id = CourseKeyField(max_length=255, db_index=True)
#     lab = models.ForeignKey(Lab, blank=True, null=True)
#     start_date = models.DateField(blank=True, null=True)
