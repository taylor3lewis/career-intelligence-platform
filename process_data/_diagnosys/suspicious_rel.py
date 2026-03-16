# coding: utf-8
from glob import glob

unique = dict()
suspicious_pair = ['jquery', 'c']

for f in glob('../data/*.csv'):
    fl = open(f, 'r')
    fl_lines = fl.readlines()
    fl.close()
    single_pairs = set()
    count = 0
    for line in fl_lines:
        line = line.strip('\n').split('|')
        if len(line) == 5:
            terms = line[-1].split(' ')
            match = 0
            for term in terms:
                if term in suspicious_pair:
                    match += 1
            if match == len(suspicious_pair):
                print(line[3], '\n', line[-1], '\n')
