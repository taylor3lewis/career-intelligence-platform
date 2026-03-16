# coding: utf-8

from glob import glob

from process_data.terms_pool import TERMS

unique = dict()

for f in glob('../data/*.csv'):
    fl = open(f, 'r')
    fl_lines = fl.readlines()
    fl.close()
    single_pairs = set()
    count = 0
    for line in fl_lines:
        terms = line.split('|')[-1].split(' ')
        for term in terms:
            if term in TERMS:
                if term not in unique:
                    unique[term] = 0
                unique[term] += 1

for key, value in sorted(unique.items(), key=lambda item: (item[1], item[0]), reverse=True):
    print(value, key)
