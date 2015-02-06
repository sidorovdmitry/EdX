from PIL import Image
from functools import partial
import StringIO
import io
import requests

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand

from cache_toolbox.core import del_cached_content
from xmodule.contentstore.content import StaticContent
from xmodule.contentstore.django import contentstore
from xmodule.course_module import CourseDescriptor
from xmodule.modulestore.django import modulestore
from util.parsing_utils import course_image_url


def update_demo_course(user, course):
    updated = False

    if course.is_browsable:
        course.labster_demo = True
        updated = True
    elif course.labster_demo:
        course.is_browsable = True
        updated = True

    if updated:
        mstore = modulestore()
        mstore.update_item(course, user.id)


def upload_image(course_key, upload_file):
    filename = upload_file.name
    mime_type = upload_file.content_type

    content_loc = StaticContent.compute_location(course_key, filename)

    chunked = upload_file.multiple_chunks()
    sc_partial = partial(StaticContent, content_loc, filename, mime_type)
    if chunked:
        content = sc_partial(upload_file.chunks())
        tempfile_path = upload_file.temporary_file_path()
    else:
        content = sc_partial(upload_file.read())
        tempfile_path = None

    # first let's see if a thumbnail can be created
    (thumbnail_content, thumbnail_location) = contentstore().generate_thumbnail(
        content,
        tempfile_path=tempfile_path
    )

    # delete cached thumbnail even if one couldn't be created this time (else
    # the old thumbnail will continue to show)
    del_cached_content(thumbnail_location)
    # now store thumbnail location only if we could create it
    if thumbnail_content is not None:
        content.thumbnail_location = thumbnail_location

    # then commit the content
    contentstore().save(content)
    del_cached_content(content.location)

    return filename


def get_upload_file(response, url):
    name = url.split('/')[-1]
    content = response.content
    content_type = response.headers.get('content-type')

    return SimpleUploadedFile(name, content, content_type)


def upload_new_image(course_id, name, content_type, content):
    the_file = SimpleUploadedFile(name, content, content_type)
    upload_image(course_id, the_file)


def resize_image(user, course, base_path):
    url = "{}{}".format(base_path, course_image_url(course))

    resp = requests.get(url)
    img = Image.open(io.BytesIO(resp.content))
    if img.format == 'JPEG':
        output = StringIO.StringIO()
        img.save(output, 'jpeg', quality=80, progressive=True)
        content = output.getvalue()
        output.close()

        name = url.split('/')[-1]
        content_type = resp.headers.get('content-type')
        upload_new_image(course.id, name, content_type, content)


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            action_type = args[0]
        except IndexError:
            action_type = 'all'

        try:
            base_path = args[1]
        except IndexError:
            base_path = "http://localhost:8000"

        user = User.objects.get(id=19)
        courses = modulestore().get_courses()
        courses = [c for c in courses if isinstance(c, CourseDescriptor)]
        for course in courses:
            if action_type in ['demo', 'all']:
                update_demo_course(user, course)

            if action_type in ['image', 'all']:
                if course.labster_demo and course.is_browsable:
                    resize_image(user, course, base_path=base_path)
