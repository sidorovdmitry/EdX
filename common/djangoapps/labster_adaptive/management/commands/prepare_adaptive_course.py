import csv

from lxml import etree
import requests

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from courseware.courses import get_course_by_id
from opaque_keys.edx.locations import SlashSeparatedCourseKey

from labster.constants import ADMIN_USER_ID
from labster.models import LabProxy, ProblemProxy
from labster.parsers.problem_parsers import QuizParser
from labster.quiz_blocks import (
    QUIZ_BLOCK_S3_PATH, get_modulestore, create_xblock, update_problem,
    get_hashed_question, quizblock_xml_to_unit)
from labster_adaptive.models import Scale, Category, Problem, Answer

# DISPLAY_NAME = 'LabsterX Adaptive'
# COURSE_ID = 'LabsterX/Adaptive/2014_A'
# SECTION = 'Adaptive'
# SUB_SECTION = 'Adaptive Lab'


class Command(BaseCommand):

    def handle(self, *args, **options):
        # if len(args) < 3:
        #     self.stdout.write("args are course_id setion_name sub_section_name")
        #     return

        # course_id = args[0]
        # section_name = args[1]
        # sub_section_name = args[2]

        course_id = 'LabsterX/AdaptiveCytogenetics/2014'
        section_name = 'Cytogenetics Class'
        sub_section_name = 'Cytogenetics Lab'
        pre_test = 'Cyto-Pre-Test'
        post_test = 'Cyto-Post-Test'

        user = User.objects.get(id=ADMIN_USER_ID)

        # fetch course
        org, number, run = course_id.split('/')
        course_key = SlashSeparatedCourseKey(org, number, run)
        course = get_course_by_id(course_key)

        # fectch section and sub section
        section_dicts = {section.display_name: section for section in course.get_children()}
        course_location = course.location.to_deprecated_string()

        section = section_dicts[section_name]

        section_location = section.location.to_deprecated_string()
        sub_section_dicts = {sub.display_name: sub for sub in section.get_children()}

        sub_section = sub_section_dicts[sub_section_name]

        # delete all quizblock
        for unit in sub_section.get_children():
            get_modulestore().delete_item(unit.location, user.id)

        lab_proxy = LabProxy.objects.get(location=str(sub_section.location))
        lab = lab_proxy.lab

        def adaptive_problems(category_name, quizblock_name):
            problems = Problem.objects.filter(categories__name=category_name).order_by('order')
            unit = create_xblock(user, 'vertical', lab_proxy.location, name=quizblock_name)
            unit_location = unit.location.to_deprecated_string()

            for problem_obj in problems:
                component_name = problem_obj.item_number
                platform_xml = problem_obj.platform_xml
                platform_xml_string = problem_obj.platform_xml_string
                quiz_parser = QuizParser(problem_obj.platform_xml)
                edx_xml_string = quiz_parser.parsed_as_string

                extra_post = {'boilerplate': "multiplechoice.yaml"}
                problem = create_xblock(user, 'problem', unit_location, extra_post=extra_post)

                update_problem(
                    user,
                    problem,
                    data=edx_xml_string,
                    name=component_name,
                    platform_xml=platform_xml_string,
                    correct_index=quiz_parser.correct_index,
                    correct_answer=quiz_parser.correct_answer,
                )

                problem = get_modulestore().get_item(problem.location)
                get_modulestore().publish(problem.location, user.id)

                # create ProblemProxy
                question = problem_obj.question
                hashed = get_hashed_question(question)
                quiz_id = component_name
                obj, created = ProblemProxy.objects.get_or_create(
                    lab_proxy=lab_proxy,
                    quiz_id=quiz_id,
                    defaults={'location': str(problem.location)},
                )

                if not obj.question_text:
                    obj.question_text = question

                if obj.location != str(problem.location):
                    obj.location = str(problem.location)

                obj.question = hashed
                obj.save()

            get_modulestore().publish(unit.location, user.id)

        # pre
        adaptive_problems(pre_test, 'QuizblockPreTest')

        # main
        quizblock_xml = QUIZ_BLOCK_S3_PATH.format(lab.final_quiz_block_file)
        response = requests.get(quizblock_xml)
        assert response.status_code == 200, "missing quizblocks xml"

        tree = etree.fromstring(response.content)
        for quizblock in tree.getchildren():
            quizblock_xml_to_unit(quizblock, user, lab_proxy)

        # post
        adaptive_problems(post_test, 'QuizblockPostTest')
