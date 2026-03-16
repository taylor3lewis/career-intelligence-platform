# -*- coding: utf-8 -*-

import hashlib
from glob import glob

import db_utils
from terms_pool import TERMS

unique_data: set[str] = set()
good_lines = 0
bad_lines = 0
duplicated = 0
matches = 0
count = 0
salary_range: set[str] = set()
outliers: set[str] = set()
unique: set[str] = set()

SKILL_NEEDED = "SKILL_NEEDED"


def md5_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def main() -> None:
    for file_path in glob("data/*.csv"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file_:
            for raw_line in file_:
                line = raw_line.strip("\n")
                line = line.replace(r"\|", " ")
                parts = line.split("|")

                if len(parts) != 5:
                    continue

                job_hash = md5_hash(parts[1])

                if job_hash in unique:
                    continue

                unique.add(job_hash)

                terms = [term for term in parts[-1].split(" ") if term in TERMS]

                for term in terms:
                    db_utils.create_relationship(job_hash, term, SKILL_NEEDED)
                    print(job_hash, term)


if __name__ == "__main__":
    main()
