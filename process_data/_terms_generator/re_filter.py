# coding: utf-8

from nltk.corpus import stopwords
from nltk.corpus import words

sw_english = {k: None for k in words.words()}
sw_english2 = {k: None for k in stopwords.words()}
from custom_libs.toth import toth

accepted = open('ACCEPTED.txt', 'r')
re_accepted = open('re_ACCEPTED.txt', 'w')
re_rejected = open('re_REJECTED.txt', 'w')

for term in accepted.readlines():
    term = term.strip('\n')
    if not toth.is_stop_word(term.lower()) and term.lower() not in sw_english and term.lower() not in sw_english2:
        re_accepted.write(term + '\n')
    else:
        re_rejected.write(term + '\n')

re_accepted.close()
re_rejected.close()
