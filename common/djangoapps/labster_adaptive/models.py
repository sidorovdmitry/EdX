from django.db import models

from labster.models import Lab


class Scale(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name


class Problem(models.Model):
    lab = models.ForeignKey(Lab)
    item_number = models.CharField(max_length=50)

    ANSWER_TYPE_CHOICES = (
        (1, 'dichotomous'),
        (2, '3 response options'),
        (3, '4 response options'),
        # (4, '5 response options'),
        # (5, '6 response options'),
    )
    answer_type = models.IntegerField(choices=ANSWER_TYPE_CHOICES)
    number_of_destractors = models.IntegerField()
    question = models.TextField()
    content = models.TextField(default="")
    time = models.FloatField(blank=True, null=True)
    cd_time = models.FloatField(blank=True, null=True)
    discrimination = models.IntegerField(blank=True, null=True)
    guessing = models.FloatField(blank=True, null=True)

    scale = models.ManyToManyField(Scale, blank=True)
    station = models.ManyToManyField(Station, blank=True)


class Answer(models.Model):
    problem = models.ForeignKey(Problem)
    answer = models.TextField()
    difficulty = models.IntegerField(blank=True, null=True)
