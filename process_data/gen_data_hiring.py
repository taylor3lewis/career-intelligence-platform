# coding: utf-8
from glob import glob

unique_data = set()
good_lines = 0
bad_lines = 0
duplicated = 0
matches = 0
MINIMUM_SALARY = 900
count = 0

# data_mass = open('data_hiring.txt', 'w')

for f in glob('data/*.csv'):
    print(f)
    file_ = open(f, 'r')
    for line in file_.readlines():
        line = line.strip('\n')
        line = line.replace('\|', ' ')
        line = line.split('|')
        if len(line) == 5:
            hiring = 'INDEFINIDO'
            terms = line[-1].split(' ')
            if 'clt' in terms:
                hiring = 'CLT'
            if 'pj' in terms:
                hiring = 'PJ'
            if hiring != 'INDEFINIDO':
                print(hiring, line[1])
                count += 1
print(count)
