from django.db import models
from django.utils import timezone

from xmodule.course_module import CourseDescriptor
from xmodule.modulestore.django import modulestore
from xmodule_django.models import CourseKeyField

from labster.models import Lab, Problem
from labster_search.utils import get_sentences_from_xml, get_keywords_from_sentences


class LabKeyword(models.Model):

    lab = models.ForeignKey(Lab, blank=True, null=True)
    course_id = CourseKeyField(max_length=255, db_index=True, blank=True, null=True)

    keyword = models.CharField(max_length=255, db_index=True)
    display_name = models.CharField(max_length=255, blank=True, default="")
    rank = models.IntegerField(default=0)
    frequency = models.IntegerField(default=0, db_index=True)

    KEYWORD_PRIMARY = 1
    KEYWORD_SECONDARY = 2
    KEYWORD_TYPES = (
        (KEYWORD_PRIMARY, 'primary'),
        (KEYWORD_SECONDARY, 'secondary'),
    )
    keyword_type = models.IntegerField(choices=KEYWORD_TYPES, default=KEYWORD_PRIMARY)

    SOURCE_PROBLEM = 1
    SOURCE_ENGINE_XML = 2
    SOURCE_MANUAL = 3
    SOURCE_COURSE = 4
    SOURCES = (
        (SOURCE_PROBLEM, 'problem'),
        (SOURCE_ENGINE_XML, 'engine XML'),
        (SOURCE_MANUAL, 'manual'),
        (SOURCE_COURSE, ' course'),
    )
    source = models.IntegerField(choices=SOURCES, blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return "{}".format(self.id)

    def save(self, *args, **kwargs):
        self.keyword = self.keyword.lower()
        self.modified_at = timezone.now()
        super(LabKeyword, self).save(*args, **kwargs)


def get_keywords_from_lab_problems(lab):
    problems = Problem.get_by_lab(lab)
    sentences = [lab.name]
    sentences.extend([problem.sentence for problem in problems])
    return get_keywords_from_sentences(sentences)


def update_lab_keywords(lab, keywords, keyword_type, source):
    for keyword in keywords:
        obj, created = LabKeyword.objects.get_or_create(
            lab=lab,
            keyword=keyword,
            keyword_type=keyword_type)

        obj.frequency += 1
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


def update_lab_keyword_content(lab):
    LabKeyword.objects.filter(lab=lab).delete()
    update_lab_keywords_from_problems(lab)
    update_lab_keywords_from_xml(lab)


def update_all_lab_keywords():
    for lab in Lab.objects.all():
        update_lab_keyword_content(lab)


def get_keywords_from_course(course):
    sentences = [course.display_name]
    keywords = get_keywords_from_sentences(sentences)
    print keywords
    return keywords


def update_course_keywords(course, keywords, keyword_type, source):
    for keyword in keywords:
        obj, created = LabKeyword.objects.get_or_create(
            course_id=course.id,
            keyword=keyword,
            keyword_type=keyword_type)

        obj.frequency += 1
        obj.source = source
        obj.save()


def update_lab_keywords_from_course(course):
    keywords = get_keywords_from_course(course)
    update_course_keywords(
        course,
        keywords,
        keyword_type=LabKeyword.KEYWORD_SECONDARY,
        source=LabKeyword.SOURCE_COURSE,
    )


def update_lab_keywords_from_courses():
    courses = modulestore().get_courses()
    courses = [c for c in courses if isinstance(c, CourseDescriptor)]
    courses = [course for course in courses if course.labster_demo and course.is_browsable]
    for course in courses:
        update_lab_keywords_from_course(course)
