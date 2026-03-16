#!/usr/bin/python
# -*- coding: utf-8 -*-

import db_utils

TECH_TERM = 'TechTerm'

if __name__ == '__main__':
    fi = open('dirty.txt', 'r')
    f_lines = fi.readlines()
    fi.close()

    for t in f_lines:
        t = t.strip('\n').split(' ')[1]
        qr = "MATCH (n:TechTerm)-[r]-(m) WHERE n.nid='%s' DELETE r;"
        db_utils.execute_query(qr % t)
        print(qr % t)

        qn = "MATCH (n:TechTerm) WHERE n.nid='%s' DELETE n;"
        db_utils.execute_query(qn % t)
        print(qn % t)
