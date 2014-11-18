from lxml import etree

from django.contrib.auth.models import User

from xmodule.modulestore.django import modulestore

from labster.masters import get_problem_as_platform_xml
from labster.models import LabProxy, QuizBlockProxy, ProblemProxy
from labster.models import QuizBlock, Problem
from labster.parsers.problem_parsers import QuizParser
from labster.quiz_blocks import create_xblock, update_problem


USER_ID = 19  # kriwil@gmail.com


def prepare_lab(lab, location):
    user = User.objects.get(id=USER_ID)

    lab_proxy, _ = LabProxy.objects.get_or_create(
        lab=lab, location=location)

    lab_proxy.is_active = True
    lab_proxy.save()

    # quizblocks
    quiz_blocks = QuizBlock.objects.filter(lab=lab, is_active=True)
    for quiz_block in quiz_blocks:

        try:
            quiz_block_proxy = QuizBlockProxy.objects.get(
                lab_proxy=lab_proxy, quiz_block=quiz_block)
        except QuizBlockProxy.DoesNotExist:
            quiz_block_proxy = QuizBlockProxy(
                lab_proxy=lab_proxy, quiz_block=quiz_block)

        # create unit
        unit = create_unit_from_quiz_block_proxy(
            user, quiz_block_proxy, lab_proxy.location)

        quiz_block_proxy.is_active = True
        quiz_block_proxy.location = unit.location
        quiz_block_proxy.save()

        problems = Problem.objects.filter(quiz_block=quiz_block, is_active=True)
        for problem in problems:
            try:
                problem_proxy = ProblemProxy.objects.get(
                    quiz_block_proxy=quiz_block_proxy,
                    problem=problem)
            except ProblemProxy.DoesNotExist:
                problem_proxy = ProblemProxy(
                    quiz_block_proxy=quiz_block_proxy,
                    problem=problem)

            # create component
            component = create_component_from_problem_proxy(
                user, problem_proxy, unit.location)

            problem_proxy.is_active = True
            problem_proxy.location = component.location
            problem_proxy.save()

            component = modulestore().get_item(component.location)
            modulestore().publish(component.location, user.id)

        unit = modulestore().get_item(unit.location)
        modulestore().publish(unit.location, user.id)


def create_unit_from_quiz_block_proxy(user, quiz_block_proxy, location):
    name = quiz_block_proxy.quiz_block.element_id
    unit = create_xblock(user, 'vertical', location, name=name)
    return unit


def create_component_from_problem_proxy(user, problem_proxy, location):
    name = problem_proxy.problem.element_id
    extra_post = {'boilerplate': "multiplechoice.yaml"}
    component = create_xblock(
        user, 'problem', location.to_deprecated_string(), extra_post=extra_post)

    platform_xml = get_problem_as_platform_xml(problem_proxy.problem)
    quiz_parser = QuizParser(platform_xml)
    edx_xml = quiz_parser.parsed_as_string

    update_problem(
        user,
        component,
        data=edx_xml,
        name=component.name,
        platform_xml=etree.tostring(platform_xml, pretty_print=True),
        correct_index=quiz_parser.correct_index,
        correct_answer=quiz_parser.correct_answer,
    )

    return component
