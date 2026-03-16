#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

import db_utils
from terms_pool import TERMS

REQUIREMENT = "REQUIREMENT"


def main() -> None:
    count = 0
    begin = datetime.now()

    with open("data_combinations.txt", "r", encoding="utf-8", errors="ignore") as data_mass:
        lines = data_mass.readlines()

    for relations in lines:
        relations = relations.strip("\n").strip().split(" ")

        if len(relations) <= 1:
            continue

        count += 1
        unique_pairs: set[tuple[str, str]] = set()

        for item in relations:
            for other in relations:
                if item != other and item in TERMS:
                    unique_pairs.add(tuple(sorted([item, other])))

        for pair in sorted(unique_pairs):
            db_utils.relationship_incremental_count(pair[0], pair[1], REQUIREMENT)

        diff = datetime.now() - begin

        print(
            count,
            "items | rodando há",
            str(diff).split(".")[0],
            "| média atual por linha",
            str(diff / count),
            "| previsão",
            str((diff / count) * len(lines)).split(".")[0],
        )

        with open("breakpoint.txt", "w", encoding="utf-8") as break_point:
            break_point.write(str(count))


if __name__ == "__main__":
    main()
