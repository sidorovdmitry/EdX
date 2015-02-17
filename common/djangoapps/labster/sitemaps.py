from django.conf import settings
from django.contrib.sitemaps import Sitemap


class Page(object):

    def __init__(self, *args, **kwargs):
        self.url = kwargs.get('url', '')

    def get_absolute_url(self):
        return self.url


def all_pages():
    pages = []
    for key, value in settings.MKTG_URL_LINK_MAP.items():
        if value is None:
            continue

        if key == "ROOT":
            continue

        pages.append(Page(url="/{}".format(value)))

    return pages


class PageSitemap(Sitemap):
    def items(self):
        return all_pages()
