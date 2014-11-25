from datetime import timedelta
from unittest import TestCase

from factory.django import DjangoModelFactory
import factory
import mock

from django.utils import timezone

from labster.models import Lab, LabProxy, Problem, Answer, QuizBlock, AdaptiveProblem


class LabFactory(DjangoModelFactory):
    FACTORY_FOR = Lab


class LabProxyFactory(DjangoModelFactory):
    FACTORY_FOR = LabProxy
    lab = factory.SubFactory(LabFactory)


class QuizBlockFactory(DjangoModelFactory):
    FACTORY_FOR = QuizBlock
    lab = factory.SubFactory(LabFactory)


class ProblemFactory(DjangoModelFactory):
    FACTORY_FOR = Problem
    quiz_block = factory.SubFactory(QuizBlockFactory)


class AnswerFactory(DjangoModelFactory):
    FACTORY_FOR = Answer
    problem = factory.SubFactory(ProblemFactory)


class LabModelTest(TestCase):

    @mock.patch('labster.masters.fetch_quizblocks')
    def test_fetch_sith_lab_proxies(self, fn):
        lab_proxy = LabProxyFactory()
        lab = lab_proxy.lab

        labs = Lab.fetch_with_lab_proxies()
        self.assertTrue(labs.exists())
        for lab in labs:
            self.assertEqual(lab.labproxy_count, 1)

    @mock.patch('labster.masters.fetch_quizblocks')
    def test_update_quiz_block_last_updated(self, fn):
        sometimes = timezone.now() - timedelta(days=7)
        lab = LabFactory(quiz_block_last_updated=sometimes)

        Lab.update_quiz_block_last_updated(lab.id)
        lab = Lab.objects.get(id=lab.id)
        self.assertGreater(lab.quiz_block_last_updated, sometimes)

    def test_slug(self):
        lab = Lab()
        lab.engine_xml = 'Engine_SpiderMan.xml'
        self.assertEqual(lab.slug, 'SpiderMan')

    def test_slug_no_engine_xml(self):
        lab = Lab()
        self.assertEqual(lab.slug, '')


class ProblemModelTest(TestCase):

    @mock.patch('labster.masters.fetch_quizblocks')
    def test_correct_answers(self, fn):
        answer = AnswerFactory(is_correct=True)
        problem = answer.problem
        self.assertIn(answer, problem.correct_answers)

    @mock.patch('labster.masters.fetch_quizblocks')
    def test_no_correct_answers(self, fn):
        answer = AnswerFactory()
        problem = answer.problem
        self.assertNotIn(answer, problem.correct_answers)
