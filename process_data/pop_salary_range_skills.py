# coding: utf-8
import re
from glob import glob

import db_utils

unique_data = set()
good_lines = 0
bad_lines = 0
duplicated = 0
matches = 0
MINIMUM_SALARY = 900
data_mass = open('data_mass_salary.txt', 'w')
step = 1000
count = 0
salary_range = set()
outliers = set()

for f in glob('data/*.csv'):
    # print f
    file_ = open(f, 'r')
    for line in file_.readlines():
        line = line.strip('\n')
        line = line.replace('\|', ' ')
        # line = line.replace('r r ', '')
        # line = line.replace('salário r ', '')
        # line = line.replace('clt r ', '')
        line = line.split('|')
        if len(line) == 5:
            salary_chunk = re.findall("([Rr]\$[\s0-9.,]+)", line[2])
            if salary_chunk:
                count += 1
                good_lines += 1
                salary_chunk = [s.strip().split(',')[0] for s in salary_chunk]
                salary_chunk = [int(re.sub(r"[Rr$\s.]", '', s)) for s in salary_chunk]

                above_salary_chunk_min = [s for s in salary_chunk if s > MINIMUM_SALARY]

                if above_salary_chunk_min:
                    mean = sum(above_salary_chunk_min) / len(above_salary_chunk_min)
                    if mean > 20000:
                        if 'anual' in line[2].lower() or 'ano' in line[2].lower():
                            mean = mean / 12
                    if mean > 100000:
                        # print '-'*100
                        # print above_salary_chunk_min, line[2], '| mean', mean
                        continue
                    salary_range.add(mean)
                # else:
                #   # Estágio
                # if sum(salary_chunk) >= MINIMUM_SALARY / 2:
                #     print salary_chunk, sum(salary_chunk) / len(salary_chunk)

salary_range = [[(i - 1) * step if i != 1 else 0, (i * step) + step] for i in range(1, max(salary_range) / 2000, 2)]
salary_range = [['de_' + str(r[0]) + '_a_' + str(r[1]), sum(r) / 2] for r in salary_range]

for sr in salary_range:
    db_utils.create_node(sr[0], 'SalaryRange', additional_params={'value': sr[1]})

# print count, max(salary_range), min(salary_range)
# print max(salary_range) / 2000
