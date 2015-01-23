from django.db import models
from django.utils import timezone

from labster.models import Lab, Problem
from labster_search.utils import get_keywords, get_sentences_from_xml, get_keywords_from_sentences


class LabKeyword(models.Model):

    lab = models.ForeignKey(Lab)
    keyword = models.CharField(max_length=255, db_index=True)
    rank = models.IntegerField(default=0)

    KEYWORD_PRIMARY = 1
    KEYWORD_SECONDARY = 2
    KEYWORD_TYPES = (
        (KEYWORD_PRIMARY, 'primary'),
        (KEYWORD_SECONDARY, 'secondary'),
    )
    keyword_type = models.IntegerField(choices=KEYWORD_TYPES, default=KEYWORD_PRIMARY)

    SOURCE_PROBLEM = 1
    SOURCE_ENGINE_XML = 2
    SOURCES = (
        (SOURCE_PROBLEM, 'problem'),
        (SOURCE_ENGINE_XML, 'engine XML'),
    )
    source = models.IntegerField(choices=SOURCES, blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('lab', 'keyword', 'keyword_type')

    def __unicode__(self):
        return "{}".format(self.id)

    def save(self, *args, **kwargs):
        self.keyword = self.keyword.lower()
        self.modified_at = timezone.now()
        super(LabKeyword, self).save(*args, **kwargs)


def get_keywords_from_lab_problems(lab):
    problems = Problem.get_by_lab(lab)
    sentences = [problem.sentence for problem in problems]
    return get_keywords_from_sentences(sentences)


def update_lab_keywords(lab, keywords, keyword_type, source):
    for keyword in keywords:
        obj, _ = LabKeyword.objects.get_or_create(
            lab=lab,
            keyword=keyword,
            keyword_type=keyword_type)
        if not obj.source:
            obj.source = source
            obj.save()


def update_lab_keywords_from_problems(lab):
    keywords = get_keywords_from_lab_problems(lab)
    update_lab_keywords(
        lab,
        keywords,
        keyword_type=LabKeyword.KEYWORD_SECONDARY,
        source=LabKeyword.SOURCE_PROBLEM,
    )


def update_lab_keywords_from_xml(lab):
    sentences = get_sentences_from_xml(lab.engine_xml_url)
    keywords = get_keywords_from_sentences(sentences)

    update_lab_keywords(
        lab,
        keywords,
        keyword_type=LabKeyword.KEYWORD_SECONDARY,
        source=LabKeyword.SOURCE_ENGINE_XML,
    )


def update_all_lab_keywords(delete_all=False):
    if delete_all:
        LabKeyword.objects.all().delete()

    for lab in Lab.objects.all():
        update_lab_keywords_from_problems(lab)
        update_lab_keywords_from_xml(lab)
