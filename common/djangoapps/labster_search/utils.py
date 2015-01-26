import bleach
import re
import requests

from lxml import etree

BANNED_WORDS = [
    'all',
    'and',
    'are',
    'can',
    'for',
    'have',
    'lab',
    'that',
    'the',
    'this',
    'with',
    'you',
]


def clean_string(string):
    return re.sub('[\(\)\?!,.]+', '', string)


def get_keywords(text):
    """
    Get list of word from text
    """
    words = []
    for word in text.split():
        word = bleach.clean(word, strip=True)
        word = clean_string(word).strip().lower()
        if word and word not in BANNED_WORDS and len(word) > 2:
            words.append(word)
    return words


def get_keywords_from_sentences(sentences):
    keywords_list = [get_keywords(sentence) for sentence in sentences]
    keywords = [word for words in keywords_list for word in words]
    return keywords


def get_sentences_from_xml(url):
    response = requests.get(url)
    assert response.status_code == 200, "no XML file"

    root = etree.fromstring(response.content)
    sentences = []
    for el in root.iter():
        if el.tag == 'Conversation':
            sentence = el.attrib.get('Sentence', '')
            if sentence:
                sentences.append(sentence)

        elif el.tag == 'StartConversation':
            sentence = el.attrib.get('ConversationSentence', '')
            if sentence:
                sentences.append(sentence)

    return sentences


def uniqify(data):
    seen = set()
    seen_add = seen.add
    return [x for x in data if not (x in seen or seen_add(x))]
