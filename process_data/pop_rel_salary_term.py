#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import re
from glob import glob

import db_utils

MINIMUM_SALARY = 1000
BASE = 1000

unique_job: dict[str, None] = {}
ranges: dict[str, dict[str, int]] = {}


def md5_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def load_salary_ranges() -> dict[str, dict[str, int]]:
    loaded_ranges: dict[str, dict[str, int]] = {}

    for salary in db_utils.execute_query("MATCH (n:SalaryRange) RETURN n;"):
        node = salary[0]
        nid = node.properties["nid"]
        value = int(node.properties["value"])

        loaded_ranges[nid] = {
            "min": value - BASE,
            "max": value + BASE - 1,
        }

    return loaded_ranges


def extract_mean_salary(text: str) -> int | None:
    salary_chunk = re.findall(r"([Rr]\$[\s0-9.,]+)", text)
    if not salary_chunk:
        return None

    salary_chunk = [s.strip().split(",")[0] for s in salary_chunk]
    salary_chunk = [
        int(re.sub(r"[Rr$\s.]", "", s))
        for s in salary_chunk
        if re.sub(r"[Rr$\s.]", "", s).isdigit()
    ]

    above_salary_chunk_min = [s for s in salary_chunk if s > MINIMUM_SALARY]
    if not above_salary_chunk_min:
        return None

    mean = sum(above_salary_chunk_min) // len(above_salary_chunk_min)

    if mean > 20000 and ("anual" in text.lower() or "ano" in text.lower()):
        mean = mean // 12

    if mean > 100000:
        return None

    return mean


def main() -> None:
    global ranges
    ranges = load_salary_ranges()

    for file_path in glob("data/*.csv"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file_:
            for raw_line in file_:
                line = raw_line.strip("\n")
                line = line.replace(r"\|", " ")
                parts = line.split("|")

                if len(parts) != 5:
                    continue

                mean = extract_mean_salary(parts[2])
                if mean is None:
                    continue

                for range_id, range_data in ranges.items():
                    if range_data["max"] > mean > range_data["min"]:
                        if re.match(r"https?://", parts[1]) is not None:
                            job_hash = md5_hash(parts[1])

                            if job_hash not in unique_job:
                                unique_job[job_hash] = None
                                db_utils.create_relationship(job_hash, range_id, "SALARY_OFFER")
                                print("create", job_hash, "->", range_id)
                            else:
                                print("duplicate", job_hash)


if __name__ == "__main__":
    main()
