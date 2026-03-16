# coding: utf-8
import re

from nltk.corpus import stopwords
from unidecode import unidecode

from filter_tables import CHARS
from filter_tables import ENTITY
from filter_tables import HTML_ENTITIES
from filter_tables import NUMBS
from stop_words.adjetivos import ADJETIVOS
from stop_words.adverbios import ADVERBIOS
from stop_words.artigos import ARTIGOS
from stop_words.conjugacoes import CONJUGACOES
from stop_words.conjuncoes import CONJUNCOES
from stop_words.contracoes import CONTRACOES
from stop_words.numerais import NUMEROS
from stop_words.preposicoes import PREPOSICOES
from stop_words.substantivos import SUBSTANTIVOS
from stop_words.verbos import VERBOS

custom_stop_words = dict()
[custom_stop_words.update(category) for category in [
    ADJETIVOS, ADVERBIOS, ARTIGOS, CONJUGACOES, CONJUNCOES,
    CONTRACOES, NUMEROS, PREPOSICOES, SUBSTANTIVOS, VERBOS
]]

BAD_CHARS = dict()
[BAD_CHARS.update(table_char) for table_char in [CHARS, ENTITY, NUMBS, HTML_ENTITIES]]

stop_words = set(stopwords.words("portuguese"))


def safe_entry_point(word, lower=True):
    word = word.strip()
    if lower:
        word = word.lower()
    if not isinstance(word, str):
        word = str(word, 'utf-8')
    return word


def check_str_integrity(text):
    if not len(text) > 0:
        return False
    if not isinstance(text, str):
        text = str(text, 'utf-8', 'replace')
    result = re.findall(
        r'[^!\"#&\'()+,\-./\s0123456789:_a-zA-ZáàãâäéèêëíìîïóòõôöúùûüçñÁÀÃÂÄÉÈÊËÍÌÎÏÓÒÕÖÔÚÙÛÜÇ]',
        text,
        re.UNICODE)
    return not len(result) > 0


def check_term_integrity(text):
    if not len(text) > 0:
        return False
    if not isinstance(text, str):
        text = str(text, 'utf-8', 'replace')
    result = re.findall(
        r'[^!\"#&\'()+,\-./\s0123456789:_a-zA-ZáàãâäéèêëíìîïóòõôöúùûüçñÁÀÃÂÄÉÈÊËÍÌÎÏÓÒÕÖÔÚÙÛÜÇΑαΒβΓγΔδΕεΖζΗηΘθΙιΚκΛλΜμΝνΞξΟοΠπΡρΣσςΤτΥυΦφΧχΨψΩω]',
        text,
        re.UNICODE)
    return not len(result) > 0


def strip_non_unicode_chars(text):
    temp = text
    counter = 0
    while not check_str_integrity(temp) and counter < 10:
        counter += 1
        temp = re.sub(r'[^a-zA-ZáàãâäéèêëíìîïóòõôöúùûüçñÁÀÃÂÄÉÈÊËÍÌÎÏÓÒÕÖÔÚÙÛÜÇ\s-]', '', temp)
    if not isinstance(temp, str):
        temp = str(temp, 'utf-8', 'replace')
    return temp.replace('\ufffd', '')


def is_stop_word(word):
    word = safe_entry_point(word)
    return word in custom_stop_words or word in stop_words


def check_word_plural(word, lower=True):
    word = safe_entry_point(word, lower)
    # basic check
    if not word.endswith('s'):
        return False

    # treatment 1: just get rid of "s" # raiz - raízes
    if len(word[:-2]) > 3 and (word[:-1] in custom_stop_words
                               or word[:-2] in custom_stop_words
                               or unidecode(word[:-2]) in custom_stop_words):
        return True

    # treatment : português - portugueses
    if word[:-4] + u'ês' in custom_stop_words:
        return True

    # treatment : just get rid of "s"
    if word.endswith('s') and len(word[:-2]) > 3 and (word[:-1] in custom_stop_words or word[:-2] in custom_stop_words):
        return True

    # treatment : ão - ãos
    if word.endswith(u'ãos') and word[:-3] + u'ão' in custom_stop_words:
        return True

    # treatment : ão - ães
    if word.endswith(u'ães') and word[:-3] + u'ão' in custom_stop_words:
        return True

    # treatment : ção - ções
    if word.endswith(u'ções') and word[:-3] + u'ão' in custom_stop_words:
        return True

    # treatment : fiel - fiéis / mel - méis
    if word[:-2] + u'l' in custom_stop_words:
        return True

    # treatment : troféu - troféus
    if word.endswith(u'éus') and unidecode(word[:-2]) + u'u' in custom_stop_words:
        return True

    # treatment : gás - gases
    if word.endswith(u'es') and unidecode(word[:-4]) + u'ás' in custom_stop_words:
        return True

    # treatment : dinamarquês - dinamarqueses
    if unidecode(word[:-4]) + u'ês' in custom_stop_words:
        return True

    # treatment : canil - canis
    if unidecode(word[:-1]) + u'l' in custom_stop_words:
        return True

    # treatment : difícil - difíceis
    if word.endswith('eis') and (unidecode(word[:-3]) + u'il' in custom_stop_words
                                 or word[:-3] + u'il' in custom_stop_words):
        return True

    return False
