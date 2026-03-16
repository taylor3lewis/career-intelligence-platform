# coding: utf-8
from glob import glob
from terms_pool import TERMS

unique_data = set()
good_lines = 0
bad_lines = 0
duplicated = 0
matches = 0

data_match_filter = open('terms_generator/data_match_filter.txt', 'w')

unique_combinations = set()

for f in glob('data/*.csv'):
    print(f)
    file_ = open(f, 'r')
    for line in file_.readlines():
        line = line.strip('\n')
        line = line.replace('\|', ' ')
        line = line.replace('r r ', '')
        line = line.replace('salário r ', '')
        line = line.replace('clt r ', '')
        line = line.split('|')
        if len(line) == 5:
            good_lines += 1
            row_matches = set()
            for term in line[-1].split(' '):
                if term in TERMS:
                    row_matches.add(term)
            raw = " ".join(sorted(row_matches))
            if raw in unique_data:
                duplicated += 1
            unique_data.add(raw)
        else:
            bad_lines += 1
            continue

real_terms = set()
for data_line in sorted(unique_data):
    for t in data_line.split(' '):
        real_terms.add(t)

for rt in sorted(real_terms):
    data_match_filter.write(rt+'\n')

data_match_filter.close()

print("-" * 50)
print("|"+"REPORT".center(48, " ")+"|")
print("-" * 50)
print("| good lines".ljust(22, ' '), str(good_lines).rjust(25, ' '), '|')
print("| bad lines".ljust(22, ' '), str(bad_lines).rjust(25, ' '), '|')
print("| duplicated lines".ljust(22, ' '), str(duplicated).rjust(25, ' '), '|')
print("| utils lines".ljust(22, ' '), str(matches).rjust(25, ' '), '|')
print("-" * 50)
