#!/usr/bin/python
# -*- coding: utf-8 -*-

from glob import glob

import db_utils

TECH_TERM = 'TechTerm'

if __name__ == '__main__':
    all_terms = set()
    data_mass = open('../terms_generator/ACCEPTED.txt', 'r')
    for term in data_mass.readlines():
        all_terms.add(term.strip('\n').lower())
    data_mass.close()

    rej = dict()
    for un in all_terms:
        if db_utils.get_node(un) is None:
            rej[un] = None
            print('\r', un, end='')
    selected = set()

    print('\r')

    for f in glob('../data/*.csv'):
        print('\r', f, end='')
        fl = open(f, 'r')
        fl_lines = fl.readlines()
        fl.close()
        for line in fl_lines:
            terms = line.split('|')[-1].split(' ')
            for t in terms:
                if t in rej:
                    selected.add(t)

    print(len(selected))
    for s in sorted(selected):
        print(s)
