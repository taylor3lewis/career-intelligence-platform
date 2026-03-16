# -*- coding: utf-8 -*-

import re
from glob import glob

import db_utils

unique_data: set[str] = set()
good_lines = 0
bad_lines = 0
duplicated = 0
matches = 0

MINIMUM_SALARY = 900
STEP = 1000

count = 0
salary_values: set[int] = set()
outliers: set[int] = set()


def extract_salary_numbers(text: str) -> list[int]:
    salary_chunk = re.findall(r"([Rr]\$[\s0-9.,]+)", text)
    if not salary_chunk:
        return []

    salary_chunk = [s.strip().split(",")[0] for s in salary_chunk]
    salary_chunk = [int(re.sub(r"[Rr$\s.]", "", s)) for s in salary_chunk if re.sub(r"[Rr$\s.]", "", s).isdigit()]
    return salary_chunk


def normalize_salary_mean(values: list[int], text: str) -> int | None:
    above_min = [s for s in values if s > MINIMUM_SALARY]
    if not above_min:
        return None

    mean = sum(above_min) // len(above_min)

    if mean > 20000 and ("anual" in text.lower() or "ano" in text.lower()):
        mean = mean // 12

    if mean > 100000:
        print("-" * 100)
        print(above_min, text, "| mean", mean)
        return None

    return mean


def build_salary_ranges(values: set[int], step: int) -> list[str]:
    if not values:
        return []

    max_value = max(values)
    ranges = [
        [((i - 1) * step) if i != 1 else 0, (i * step) + step]
        for i in range(1, max_value // 2000, 2)
    ]
    return [f"de_{start}_a_{end}" for start, end in ranges]


def main() -> None:
    global count, good_lines

    for file_path in glob("data/*.csv"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file_:
            for raw_line in file_:
                line = raw_line.strip("\n")
                line = line.replace(r"\|", " ")
                parts = line.split("|")

                if len(parts) != 5:
                    continue

                salary_numbers = extract_salary_numbers(parts[2])
                if not salary_numbers:
                    continue

                count += 1
                good_lines += 1

                mean = normalize_salary_mean(salary_numbers, parts[2])
                if mean is not None:
                    salary_values.add(mean)

    salary_ranges = build_salary_ranges(salary_values, STEP)

    for salary_range in salary_ranges:
        print(salary_range)
        db_utils.create_node(salary_range, "SalaryRange")


if __name__ == "__main__":
    main()
