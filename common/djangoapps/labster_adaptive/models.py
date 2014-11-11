from django.db import models
from django.utils import timezone

from labster.models import Lab


class Scale(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name


class Problem(models.Model):
    item_number = models.CharField(max_length=50, unique=True)

    ANSWER_TYPE_CHOICES = (
        (1, 'dichotomous'),
        (2, '3 response options'),
        (3, '4 response options'),
        # (4, '5 response options'),
        # (5, '6 response options'),
    )
    answer_type = models.IntegerField(choices=ANSWER_TYPE_CHOICES, blank=True, null=True)
    number_of_destractors = models.IntegerField(blank=True, null=True)
    question = models.TextField()
    content = models.TextField(default="")
    feedback = models.TextField(default="")
    time = models.FloatField(blank=True, null=True)
    sd_time = models.FloatField(blank=True, null=True)
    discrimination = models.IntegerField(blank=True, null=True)
    guessing = models.FloatField(blank=True, null=True)
    order = models.IntegerField(default=0)
    image_url = models.URLField(max_length=500, blank=True, default="")

    scales = models.ManyToManyField(Scale, blank=True)
    categories = models.ManyToManyField(Category, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('order',)

    def __unicode__(self):
        return self.question


class Answer(models.Model):
    problem = models.ForeignKey(Problem)
    answer = models.TextField()
    difficulty = models.IntegerField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return "{}: {}".format(self.problem, self.answer)
