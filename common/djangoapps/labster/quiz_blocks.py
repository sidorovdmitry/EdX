import hashlib
import json

from lxml import etree
import requests

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone

from labster.constants import COURSE_ID, ADMIN_USER_ID
from labster.models import Lab, ProblemProxy, LabProxy, Problem
from labster.parsers.problem_parsers import QuizParser
from labster.utils import get_request

QUIZ_BLOCK_S3_PATH = "https://s3-us-west-2.amazonaws.com/labster/uploads/{}"
SECTION_NAME = 'Labs'


def get_usage_key():
    from opaque_keys.edx.keys import UsageKey
    return UsageKey


def get_modulestore():
    from xmodule.modulestore.django import modulestore
    return modulestore()


def get_master_course(user=None, command=None):
    from contentstore.utils import add_instructor, initialize_permissions
    from courseware.courses import get_course_by_id
    from opaque_keys.edx.locations import SlashSeparatedCourseKey
    from student.roles import CourseRole
    from xmodule.modulestore.exceptions import InvalidLocationError

    if not user:
        user = User.objects.get(id=ADMIN_USER_ID)

    display_name = "LabsterX Master"
    org, number, run = COURSE_ID.split('/')

    try:
        course_key = SlashSeparatedCourseKey(org, number, run)
        fields = {'display_name': display_name}

        wiki_slug = u"{0}.{1}.{2}".format(course_key.org, course_key.course, course_key.run)
        definition_data = {'wiki_slug': wiki_slug}
        fields.update(definition_data)

        if CourseRole.course_group_already_exists(course_key):
            raise InvalidLocationError()

        course = get_modulestore().create_course(
            course_key.org,
            course_key.course,
            course_key.run,
            user.id,
            fields=fields,
        )

        # Make sure user has instructor and staff access to the new course
        add_instructor(course.id, user, user)

        # Initialize permissions for user in the new course
        initialize_permissions(course.id, user)
        command and command.stdout.write("name: {}\n".format(course.display_name))

    except InvalidLocationError:
        course = get_course_by_id(course_key)

    return course


def get_master_sections(user=None, course=None, command=None):
    """
    return section_location and sub_section_dicts

    this used to create master quizblocks and quizzes
    """
    section_name = SECTION_NAME
    if not user:
        user = User.objects.get(id=ADMIN_USER_ID)
    if not course:
        course = get_master_course(user=user, command=command)

    section_dicts = {section.display_name: section for section in course.get_children()}
    course_location = course.location.to_deprecated_string()

    # create the section if the defined section doesn't exist yet
    # most of the time, this shouldn't happen since usually we're just create
    # the section manually
    if section_name not in section_dicts:
        # command and command.stdout.write("creating {}\n".format(section_name))
        section_dicts[section_name] = create_xblock(user, 'chapter', course_location, name=section_name)

    section = section_dicts[section_name]
    section_location = section.location.to_deprecated_string()
    sub_section_dicts = {sub.display_name: sub for sub in section.get_children()}

    return section_location, sub_section_dicts


def get_or_create_problem_proxy_from_quiz(lab_proxy, quiz, location, quiz_block_name):
    question = quiz.attrib.get('Sentence')
    quiz_id = quiz.attrib.get('Id')
    hashed = get_hashed_question(question)

    # try to use hased first
    objects = ProblemProxy.objects.filter(
        lab_proxy=lab_proxy, question=hashed).filter(
            Q(quiz_id="") | Q(quiz_id="UPDATE_THIS"))
    if objects.exists():
        obj, created = objects[0], False
        obj.quiz_id = quiz_id

    else:
        obj, created = ProblemProxy.objects.get_or_create(
            lab_proxy=lab_proxy,
            quiz_id=quiz_id,
        )

    try:
        problem = Problem.objects.get(
            quiz_block__lab=lab_proxy.lab,
            quiz_block__element_id=quiz_block_name,
            element_id=quiz_id)
    except Problem.DoesNotExist:
        problem = None
        is_active = False
    else:
        is_active = True

    obj.problem = problem
    obj.correct_answer = get_correct_answer_from_quiz(quiz)
    obj.is_active = is_active
    obj.location = location
    obj.question = hashed
    obj.question_text = question
    obj.save()

    return obj, created


def get_correct_answer_from_quiz(quiz):
    correct_answer = ''
    for options in quiz.getchildren():
        for option in options.getchildren():
            if option.attrib.get('IsCorrectAnswer') == 'true':
                correct_answer = option.attrib.get('Sentence')
    return correct_answer


def create_xblock(user, category, parent_location, name=None, extra_post=None):
    """
    Wrapper to create xblock
    """
    from contentstore.views.item import _create_item

    post_data = {
        'parent_locator': parent_location,
        'category': category,
    }

    if name:
        post_data['display_name'] = name

    if extra_post:
        post_data.update(extra_post)

    request = get_request(user, json.dumps(post_data))
    response = _create_item(request)
    response_content = json.loads(response.content)
    section_location = response_content['locator']
    usage_key = get_usage_key().from_string(section_location)
    store = get_modulestore()

    return store.get_item(usage_key)


def update_problem(user, xblock, data, name, platform_xml, correct_index=None,
                   correct_answer=''):
    """
    update 'problem' (quizblock with component type)
    """
    from contentstore.views.item import _save_xblock

    nullout = ["markdown"]
    metadata = {
        'display_name': name,
        'platform_xml': platform_xml,
        'correct_index': correct_index,
        'correct_answer': correct_answer,
    }

    response = _save_xblock(
        user,
        xblock,
        data=data,
        nullout=nullout,
        metadata=metadata,
        publish='make_public',
    )

    new_xblock = json.loads(response.content)
    locator = get_usage_key().from_string(new_xblock['id'])
    get_modulestore().publish(locator, user.id)
    return new_xblock


def update_master_lab(lab, user=None, course=None,
                      section_location=None,
                      sub_section_dicts=None,
                      command=None,
                      force_update=False):

    if not user:
        user = User.objects.get(id=ADMIN_USER_ID)

    if not course:
        course = get_master_course(user=user, command=command)
        section_location, sub_section_dicts = get_master_sections(
            user=user, course=course, command=command)

    # sub section is using lab's name as the name
    # FIXME: we should use location for this as name could be changed
    if lab.name not in sub_section_dicts:
        # command and command.stdout.write("creating {}\n".format(lab.name))
        sub_section_dicts[lab.name] = create_xblock(user, 'sequential', section_location, name=lab.name)

    elif not force_update:
        return

    quizblock_xml = QUIZ_BLOCK_S3_PATH.format(lab.quiz_block_file)
    response = requests.get(quizblock_xml)
    assert response.status_code == 200, "missing quizblocks xml"

    # parse quizblock xml and store it in the sub section
    # the quizblock xml contains quizblock and quiz
    tree = etree.fromstring(response.content)
    sub_section = sub_section_dicts[lab.name]
    sub_section_location = sub_section.location.to_deprecated_string()

    if force_update:
        unit_dicts = {}
        for qb in sub_section.get_children():
            get_modulestore().delete_item(qb.location, user.id)

    else:
        unit_dicts = {qb.display_name: qb for qb in sub_section.get_children()}

    for quizblock in tree.getchildren():
        name = quizblock.attrib.get('Id')
        if name not in unit_dicts:
            # command and command.stdout.write("creating quizblock {}\n".format(name))
            unit_dicts[name] = create_xblock(user, 'vertical', sub_section_location, name=name)

        elif not force_update:
            continue

        unit = unit_dicts[name]
        unit_location = unit.location.to_deprecated_string()
        problem_dicts = {problem.display_name: problem for problem in unit.get_children()}

        for quiz in quizblock.getchildren():
            name = quiz.attrib.get('Id')

            if name not in problem_dicts:
                # command and command.stdout.write("creating problem {}\n".format(name))
                extra_post = {'boilerplate': "multiplechoice.yaml"}
                problem_dicts[name] = create_xblock(user, 'problem', unit_location, extra_post=extra_post)

            elif not force_update:
                continue

            problem_xblock = problem_dicts[name]
            platform_xml = etree.tostring(quiz, pretty_print=True)

            quiz_parser = QuizParser(quiz)

            edx_xml = platform_xml
            update_problem(user, problem_xblock, data=edx_xml, name=name,
                           platform_xml=platform_xml,
                           correct_index=quiz_parser.correct_index,
                           correct_answer=quiz_parser.correct_answer)


def update_course_lab(user, course, section_name, sub_section_name,
                      command=None, force_update=False):

    section_dicts = {section.display_name: section for section in course.get_children()}

    section = section_dicts[section_name]
    sub_section_dicts = {sub.display_name: sub for sub in section.get_children()}

    sub_section = sub_section_dicts[sub_section_name]
    sub_section_location = sub_section.location.to_deprecated_string()
    lab_proxy = LabProxy.objects.get(location=sub_section_location)
    lab = lab_proxy.lab

    quizblock_xml = QUIZ_BLOCK_S3_PATH.format(lab.quiz_block_file)
    response = requests.get(quizblock_xml)
    assert response.status_code == 200, "missing quizblocks xml"

    # parse quizblock xml and store it in the sub section
    # the quizblock xml contains quizblock and quiz
    tree = etree.fromstring(response.content)

    if force_update:
        for qb in sub_section.get_children():
            get_modulestore().delete_item(qb.location, user.id)

    unit_dicts = {}  # qb.display_name: qb for qb in sub_section.get_children()}

    for quizblock in tree.getchildren():
        name = quizblock.attrib.get('Id')
        if name not in unit_dicts:
            # command and command.stdout.write("creating quizblock {}\n".format(name))
            unit_dicts[name] = create_xblock(user, 'vertical', sub_section_location, name=name)

        elif not force_update:
            continue

        unit = unit_dicts[name]
        unit_location = unit.location.to_deprecated_string()
        problem_dicts = {problem.display_name: problem for problem in unit.get_children()}

        for quiz in quizblock.getchildren():
            name = quiz.attrib.get('Id')

            if name not in problem_dicts:
                # command and command.stdout.write("creating problem {}\n".format(name))
                extra_post = {'boilerplate': "multiplechoice.yaml"}
                problem_dicts[name] = create_xblock(user, 'problem', unit_location, extra_post=extra_post)

            elif not force_update:
                continue

            problem_xblock = problem_dicts[name]

            platform_xml = etree.tostring(quiz, pretty_print=True)
            quiz_parser = QuizParser(quiz)

            edx_xml = platform_xml
            update_problem(user, problem_xblock, data=edx_xml, name=name,
                           platform_xml=platform_xml,
                           correct_index=quiz_parser.correct_index,
                           correct_answer=quiz_parser.correct_answer)


def update_quizblocks(
        course=None, user=None, section_name='Labs', command=None, is_master=False,
        force_update=False):

    """
    updates sub sections (quizblocks) of master course

    This function will create the section, sub section, and fetch quizblock from
    XML. This should only be used for master lab.
    """

    # FIXME
    assert is_master, "only master lab"

    if not user:
        user = User.objects.get(id=ADMIN_USER_ID)

    if not course:
        course = get_master_course(user=user, command=command)

    section_location, sub_section_dicts = get_master_sections(
        user=user, course=course, command=command)

    labs = Lab.objects.all()

    # iterates through all the labs and create it in master course if it doesn't
    # exist. it will fetch quizblocks from xml if the xml exists in s3.
    for lab in labs:
        update_master_lab(lab, user, course=course,
                          section_location=section_location,
                          sub_section_dicts=sub_section_dicts, command=command,
                          force_update=force_update)


def sync_quiz_xml(course, user, section_name='Labs', sub_section_name='',
                  command=None, lab_name=None):
    """
    updates quiz/problem content from it's problem_xml field

    it will updates the data field, parsed from problem_xml.
    and store it as well. it will also creates ProblemProxy objects if there's
    no ProblemProxy yet.
    """

    section_dicts = {section.display_name: section for section in course.get_children()}

    section = section_dicts[section_name]
    sub_section_dicts = {sub.display_name: sub for sub in section.get_children()}

    if sub_section_name:
        labs = [sub_section_name]
    else:
        labs = Lab.objects.all()
        labs = [lab.name for lab in labs]

    ProblemProxy.objects.filter(
        lab_proxy__is_active=False).update(is_active=False)

    for lab_name in labs:
        sub_section = sub_section_dicts[lab_name]
        try:
            lab = Lab.objects.get(id=sub_section.lab_id)
        except Lab.DoesNotExist:
            command and command.stdout.write("lab {} does not exist\n".format(sub_section.lab_id))
            continue

        lab_proxy, _ = LabProxy.objects.get_or_create(
            location=str(sub_section.location),
            defaults={'lab': lab},
        )

        # disable all problem proxies
        ProblemProxy.objects.filter(lab_proxy=lab_proxy).update(is_active=False)

        for qb in sub_section.get_children():
            for component in qb.get_children():

                quiz_parser = QuizParser(etree.fromstring(component.platform_xml))

                if component.correct_index == -1:
                    command and command.stdout.write("no correct index: {}\n".format(component.display_name))

                    component.correct_answer = quiz_parser.correct_answer
                    component.correct_index = quiz_parser.correct_index

                if component.data == component.platform_xml:
                    command and command.stdout.write("converting to data: {}\n".format(component.display_name))
                    component.data = quiz_parser.parsed_as_string

                get_modulestore().update_item(component, user.id)
                get_modulestore().publish(component.location, user.id)

                # create ProblemProxy
                tree = etree.fromstring(component.platform_xml)
                obj, created = get_or_create_problem_proxy_from_quiz(
                    lab_proxy, tree, str(component.location), qb.display_name)

                if created:
                    command and command.stdout.write("new ProblemProxy: {}\n".format(component.location))

            get_modulestore().publish(qb.location, user.id)
        get_modulestore().publish(sub_section.location, user.id)


def get_hashed_question(question):
    return hashlib.md5(question.encode('utf-8').strip()).hexdigest()


def get_problem_proxy_by_question(lab_proxy, question, quiz_id=None):
    """
    get ProblemProxy for given question

    it will creates all ProblemProxy if that single question doesn't
    have it. This shouldn't even happen.
    """

    obj = None
    if quiz_id:
        try:
            obj = ProblemProxy.objects.get(lab_proxy=lab_proxy, quiz_id=quiz_id)
        except ProblemProxy.DoesNotExist:
            pass
        else:
            return obj

    elif question:
        hashed = hashlib.md5(question.encode('utf-8').strip()).hexdigest()
        if not obj:
            try:
                obj = ProblemProxy.objects.get(lab_proxy=lab_proxy, question=hashed)
            except ProblemProxy.DoesNotExist:
                pass
            else:
                return obj

    # FIXME: do not do this
    locator = get_usage_key().from_string(lab_proxy.location)
    descriptor = get_modulestore().get_item(locator)

    for quiz_block in descriptor.get_children():
        for problem in quiz_block.get_children():
            tree = etree.fromstring(problem.platform_xml)
            new_obj, created = get_or_create_problem_proxy_from_quiz(
                lab_proxy, tree, str(problem.location), quiz_block.display_name)

            if hashed == new_obj.hashed:
                return new_obj

            if quiz_id == new_obj.quiz_id:
                return new_obj

    return obj


def quizblock_xml_to_unit(quizblock, user, lab_proxy, unit=None):
    unit_name = quizblock.attrib.get('Id')
    if not unit:
        unit = create_xblock(user, 'vertical', lab_proxy.location, name=unit_name)
    unit_location = unit.location.to_deprecated_string()

    for quiz in quizblock.getchildren():
        component_name = quiz.attrib.get('Id')
        extra_post = {'boilerplate': "multiplechoice.yaml"}
        problem = create_xblock(user, 'problem', unit_location, extra_post=extra_post)

        platform_xml = etree.tostring(quiz, pretty_print=True)
        quiz_parser = QuizParser(quiz)

        edx_xml = quiz_parser.parsed_as_string
        update_problem(
            user,
            problem,
            data=edx_xml,
            name=component_name,
            platform_xml=platform_xml,
            correct_index=quiz_parser.correct_index,
            correct_answer=quiz_parser.correct_answer,
        )

        problem = get_modulestore().get_item(problem.location)
        get_modulestore().publish(problem.location, user.id)

        # create ProblemProxy
        get_or_create_problem_proxy_from_quiz(
            lab_proxy, quiz, str(problem.location), unit.display_name)

    get_modulestore().publish(unit.location, user.id)


def update_lab_quiz_block(lab, user):
    UsageKey = get_usage_key()

    lab_proxies = LabProxy.objects.filter(lab=lab, is_active=True)

    quizblock_xml = QUIZ_BLOCK_S3_PATH.format(lab.quiz_block_file)
    response = requests.get(quizblock_xml)
    assert response.status_code == 200, "missing quizblocks xml"

    tree = etree.fromstring(response.content)

    for lab_proxy in lab_proxies:
        usage_key = UsageKey.from_string(lab_proxy.location)
        item = get_modulestore().get_item(usage_key)

        for unit in item.get_children():
            get_modulestore().delete_item(unit.location, user.id)

        for quizblock in tree.getchildren():
            quizblock_xml_to_unit(quizblock, user, lab_proxy)

    Lab.update_quiz_block_last_updated(lab.id)


def validate_lab_proxy(lab_proxy):
    from courseware.courses import get_course_by_id
    from xmodule.modulestore.exceptions import ItemNotFoundError

    UsageKey = get_usage_key()

    try:
        locator = UsageKey.from_string(lab_proxy.location)
        descriptor = get_modulestore().get_item(locator)
        course_key = descriptor.location.course_key
        course = get_course_by_id(course_key)
    except ItemNotFoundError:
        lab_proxy.is_active = False
        lab_proxy.save()
        return None, None, None

    the_section = the_sub_section = None
    section_name = sub_section_name = ''
    for section in course.get_children():
        for sub_section in section.get_children():
            if str(sub_section.location) == lab_proxy.location:
                section_name = section.display_name
                sub_section_name = sub_section.display_name

                the_section = section
                the_sub_section = sub_section

    if not all([section_name, sub_section_name]):
        lab_proxy.is_active = False
        lab_proxy.save()
        return None, None, None

    lab_proxy.is_active = True
    lab_proxy.save()

    return course, the_section, the_sub_section
