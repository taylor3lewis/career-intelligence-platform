# coding: utf-8
import csv
import datetime
import os
import re

import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

stop_words = set(stopwords.words("portuguese"))

PROJECT_ROOT = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])
ROOT_DATA = PROJECT_ROOT + '/daemons_data_hub/data/'


def get_soup(link):
    html = requests.get(link).content
    soup = BeautifulSoup(html, 'lxml')
    return soup


def clean_desc(desc):
    desc = re.sub(r"<!--((.+?)\n(.+?))+?-->", '', desc)
    while '  ' in desc:
        desc = desc.replace('  ', ' ')
    desc = re.sub(r"[\t\r]", ' ', desc)
    while '  ' in desc:
        desc = desc.replace('  ', ' ')
    while '\n\n' in desc:
        desc = desc.replace('\n\n', '\n')
    desc = "\n".join([line.strip() for line in desc.split('\n') if line != ' '])
    while '  ' in desc:
        desc = desc.replace('  ', ' ')
    return desc.strip()


def prepare_terms(description):
    _terms = re.sub(r"[Rr]$", ' ', description.replace('\n', ' '))
    _terms = re.sub(r"[,;<>:?!@$%*()_\-+=§\"]", ' ', _terms)
    _terms = " ".join([w.lower().strip() for w in _terms.split(' ') if w not in stop_words])
    while '  ' in _terms:
        _terms = _terms.replace('  ', ' ')
    return _terms


def clean_title(title):
    while '  ' in title:
        title = title.replace('  ', ' ')
    # title = title.replace('\n', '')
    return title


def save_data(file_name, title, link, salary, desc):
    # calling cleaning functions
    # --------------------------
    title = clean_title(title.strip())
    link = link.strip()
    salary = salary.strip()
    desc = clean_desc(desc)
    terms = prepare_terms(desc)
    print(title)

    # save data ------------------------------------------
    fold_date = ROOT_DATA + str(datetime.datetime.now()).split(' ')[0]
    if not os.path.exists(fold_date):
        os.makedirs(fold_date)
    with open(fold_date + '/' + file_name + ".csv", 'a') as csv_f:
        writer = csv.writer(csv_f, delimiter='|',
                            escapechar='\\',
                            quoting=csv.QUOTE_NONE,
                            lineterminator='\n')
        writer.writerow([
            title.encode('utf-8'),
            link.encode('utf-8'),
            salary.encode('utf-8'),
            desc.replace('\n', '\\n').encode('utf-8'),
            terms.encode('utf-8')
        ])
