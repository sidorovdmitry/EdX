import csv
import json

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from courseware.models import StudentModule, StudentModuleHistory
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from xmodule.modulestore.django import modulestore


def extract_survey(course_key, survey_keys):
    enrolled_students = User.objects.filter(
        courseenrollment__course_id=course_key,
        courseenrollment__is_active=1,
    ).prefetch_related("groups").order_by('username')

    rows = []

    headers = ["survey {}".format(i) for i in range(1, 11)] + ["Suggestion"]
    rows.append(headers)

    for student in enrolled_students:
        # row = [student.id]
        row = ["" for _ in headers]

        student_modules = StudentModule.objects.filter(
            course_id=course_key,
            student_id=student.id,
            module_type='problem',
        )

        for student_module in student_modules:
            history_entries = StudentModuleHistory.objects.filter(
                student_module=student_module
            ).latest('id')
            data = json.loads(history_entries.state)
            for display_name, survey_key in survey_keys:
                for key in data.get('input_state').keys():
                    if survey_key == key:
                        student_answers = data.get('student_answers')
                        if not student_answers:
                            continue

                        if len(student_answers) == 1:
                            row[10] = student_answers.itervalues().next()

                        elif len(student_answers) == 10:
                            for index, value in enumerate(student_answers.itervalues()):
                                answer = value[0].split('_')[1]
                                row[index] = answer

        row = filter(None, row)
        if row:
            rows.append(row)

    return rows


class Command(BaseCommand):

    def handle(self, *args, **options):
        course_id = args[0]
        file_name = "{}.csv".format(course_id.lower().replace('/', '-'))

        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_id)
        course = modulestore().get_course(course_key)

        survey_keys = []

        for section in course.get_children():
            if section.display_name.upper() != 'SURVEY':
                continue

            for sub_section in section.get_children():
                if sub_section.display_name.upper() != 'FEEDBACK SURVEY':
                    continue

                for unit in sub_section.get_children():
                    if unit.display_name.upper() != 'UNIT':
                        continue

                    for component in unit.get_children():
                        if component.plugin_name != 'problem':
                            continue

                        field_name = "{tag}-{org}-{course}-{category}-{name}_2_1"
                        field_key = {
                            'tag': 'i4x',
                            'org': component.location.org,
                            'course': component.location.course,
                            'category': component.location.category,
                            'name': component.location.name,
                        }

                        field_name = field_name.format(**field_key)
                        survey_keys.append((component.display_name, field_name))

        rows = extract_survey(course_key, survey_keys)

        with open(file_name, 'w') as csv_file:
            writer = csv.writer(csv_file)
            for row in rows:
                writer.writerow(row)
