from django.conf import settings
from django.contrib.sitemaps import Sitemap

from labster.courses import get_demo_courses


class Page(object):

    def __init__(self, *args, **kwargs):
        self.url = kwargs.get('url', '')

    def get_absolute_url(self):
        return self.url


def get_static_pages():
    pages = []
    for key, value in settings.MKTG_URL_LINK_MAP.items():
        if value is None:
            continue

        if key == "ROOT":
            continue

        pages.append(Page(url="/{}".format(value)))
    return pages


def get_courses():
    courses = get_demo_courses()

    def get_url(course):
        return "/courses/{}/about".format(course.id.to_deprecated_string())

    return [Page(url=get_url(course)) for course in courses]


class PageSitemap(Sitemap):
    def items(self):
        return get_static_pages() + get_courses()
