from lxml import etree

from django.core.exceptions import ObjectDoesNotExist

from wiki.core.exceptions import NoRootURL
from wiki.models import URLPath, Article


def remove_prefix(text):
    return text.replace('/wiki/', '')


def get_all_links(article):
    rendered = "<html>{}</html>".format(article.render())
    root = etree.fromstring(rendered)
    hrefs = []
    for element in root.iterfind(".//a"):
        href = element.attrib.get('href', '')
        if href.startswith('/wiki/'):
            hrefs.append(href)

    # slugs = map(remove_prefix, hrefs)
    # titles = map(get_article_title, slugs)
    # links = zip(hrefs, titles)

    links = zip(
        hrefs,
        map(
            get_article_title,
            map(
                remove_prefix,
                hrefs
            )
        )
    )

    return links


def get_article(slug):
    try:
        url_path = URLPath.get_by_path(slug, select_related=True)
    except (NoRootURL, ObjectDoesNotExist):
        return None

    try:
        article = Article.objects.get(id=url_path.article.id)
    except Article.DoesNotExist:
        return None

    return article


def get_article_title(slug):
    article = get_article(slug)
    if article:
        return unicode(article)
    return ''
