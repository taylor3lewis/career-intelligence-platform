brute = open('data_match_filter_untoucheable.txt', 'r')
buffer = ''

TERMS = open('../terms_pool.py', 'w')
TERMS.write("# coding: utf-8\n")

exceptions = ['B', 'C', 'D', 'J', 'R', 'S', 'T']
exceptions += [e.lower() for e in exceptions]

unique = set()
for term_u in brute.readlines():
    term_u = term_u.strip('\n').strip()
    if "'" in term_u:
        continue
    if len(term_u) == 1:
        if term_u not in exceptions:
            continue
    unique.add(term_u.lower())

for term in sorted(unique):
    print(term)
    term = term.replace('\n', '').strip()
    buffer += "'" + term + "':None,"
brute.close()

TERMS.write('TERMS = {' + buffer[:-1] + "}")
TERMS.close()
