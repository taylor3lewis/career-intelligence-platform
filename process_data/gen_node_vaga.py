# -*- coding: utf-8 -*-

import hashlib
import re
from glob import glob

import db_utils

bad = 0
good = 0

unique: set[str] = set()

for f in glob("data/*.csv"):
    with open(f, "r", encoding="utf-8", errors="ignore") as fo:
        for line in fo:
            line = line.strip("\n")
            line = line.replace(r"\|", " ")
            parts = line.split("|")

            if len(parts) == 5 and re.match(r"https?://", parts[1]) is not None:
                md5 = hashlib.md5(parts[1].encode("utf-8")).hexdigest()

                if md5 in unique:
                    continue

                good += 1
                unique.add(md5)

                db_utils.create_node(md5, "JOB")

            else:
                bad += 1

print()
print(bad)

print()
print(good)
