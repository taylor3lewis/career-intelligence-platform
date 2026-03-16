# -*- coding: utf-8 -*-

import hashlib
import sys
from datetime import datetime
from glob import glob
from pathlib import Path

import db_utils
from terms_pool import TERMS

project_path = Path(__file__).resolve().parents[1]
sys.path.append(str(project_path))

TECH_TERM = "TechTerm"
REQUIREMENT = "REQUIREMENT"
MISSING_TERM = ["sqlserver"]

unique: set[str] = set()

begin = datetime.now()


def md5_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def main() -> None:
    for node in MISSING_TERM:
        db_utils.create_node(node, TECH_TERM)

    for file_path in glob("data/*.csv"):
        single_pairs: set[tuple[str, str]] = set()

        with open(file_path, "r", encoding="utf-8", errors="ignore") as fl:
            for raw_line in fl:
                line = raw_line.strip("\n")
                line = line.replace(r"\|", " ")
                parts = line.split("|")

                if len(parts) != 5:
                    continue

                single_pairs = set()
                job_hash = md5_hash(parts[1])

                if job_hash not in unique:
                    unique.add(job_hash)
                    terms = parts[-1].split(" ")

                    for mt in MISSING_TERM:
                        test = parts[3].lower()

                        # if ' c/ ' not in test and ' c# ' not in test and (' c ' in test or ' c/c++ ' in test):
                        if " sql server " in test:
                            # db_utils.create_relationship(job_hash, mt, 'SKILL_NEEDED')
                            for term in terms:
                                if term in TERMS:
                                    if term == "c" and (" c " not in test or " c/c++ " in test):
                                        continue

                                    if mt != term:
                                        print(mt, term)
                                        single_pairs.add(tuple(sorted([mt, term])))

                for pair in single_pairs:
                    if db_utils.relationship_incremental_count(pair[0], pair[1], REQUIREMENT):
                        print(pair[0], "->", pair[1])

        print("begin:", begin, "| end:", datetime.now(), "| time :", datetime.now() - begin)


if __name__ == "__main__":
    main()
