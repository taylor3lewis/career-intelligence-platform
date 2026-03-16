#!/usr/bin/python
# -*- coding: utf-8 -*-

import db_utils

TECH_TERM = 'TechTerm'

if __name__ == '__main__':
    all_terms = set()
    data_mass = open('data_match_filter_untoucheable.txt', 'r')
    for term in data_mass.readlines():
        all_terms.add(term.strip('\n'))
    data_mass.close()

    count = 0
    for un in all_terms:
        count += 1
        db_utils.create_node(un, TECH_TERM)
        print(
            '\r', count, '/', len(all_terms),
            "ready", str(int(float(count) / float(len(all_terms)) * 100)) + "%", end=''
        )
