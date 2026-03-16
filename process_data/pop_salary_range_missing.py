# -*- coding: utf-8 -*-

import hashlib
from datetime import datetime
from glob import glob

import db_utils

TECH_TERM = "TechTerm"
REQUIREMENT = "REQUIREMENT"
MISSING_TERM = ["c#"]

unique: set[str] = set()
begin = datetime.now()


def md5_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def main() -> None:
    for node in MISSING_TERM:
        db_utils.create_node(node, TECH_TERM)

    for file_path in glob("data/*.csv"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fl:
            for raw_line in fl:
                line = raw_line.strip("\n")
                line = line.replace(r"\|", " ")
                parts = line.split("|")

                if len(parts) != 5:
                    continue

                job_hash = md5_hash(parts[1])

                if job_hash in unique:
                    continue

                unique.add(job_hash)
                terms = parts[-1].split(" ")
                test = parts[3].lower()

                for mt in MISSING_TERM:
                    if mt in terms:
                    # if "c#" in test:
                        db_utils.create_relationship(job_hash, mt, "SKILL_NEEDED")

        print("begin:", begin, "| end:", datetime.now(), "| time :", datetime.now() - begin)


if __name__ == "__main__":
    main()
