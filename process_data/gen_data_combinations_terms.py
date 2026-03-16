from pathlib import Path

from terms_pool import TERMS


def main() -> None:
    unique_data: set[str] = set()
    unique_combinations: set[str] = set()

    good_lines = 0
    bad_lines = 0
    duplicated = 0
    matches = 0

    output_path = Path("data_combinations_ex.txt")
    data_dir = Path("data")

    with output_path.open("w", encoding="utf-8") as data_mass:
        for file_path in data_dir.glob("*.csv"):
            print(file_path)

            with file_path.open("r", encoding="utf-8", errors="ignore") as file_:
                for raw_line in file_:
                    line = raw_line.rstrip("\n")
                    line = line.replace(r"\|", " ")
                    line = line.replace("r r ", "")
                    line = line.replace("salário r ", "")
                    line = line.replace("clt r ", "")

                    parts = line.split("|")

                    if len(parts) != 5:
                        bad_lines += 1
                        continue

                    good_lines += 1

                    row_matches = {
                        term
                        for term in TERMS
                        if term in parts[-1].split(" ")
                    }

                    if row_matches and len(row_matches) > 2:
                        comb = " ".join(sorted(row_matches))
                        if comb not in unique_combinations:
                            unique_combinations.add(comb)
                            matches += 1
                            data_mass.write(f"{comb}\n")

                    if parts[1] in unique_data:
                        duplicated += 1
                    else:
                        unique_data.add(parts[1])

    print("-" * 50)
    print("|" + "REPORT".center(48, " ") + "|")
    print("-" * 50)
    print(f"| {'good lines':<19}{good_lines:>28} |")
    print(f"| {'bad lines':<19}{bad_lines:>28} |")
    print(f"| {'duplicated lines':<19}{duplicated:>28} |")
    print(f"| {'utils lines':<19}{matches:>28} |")
    print("-" * 50)


if __name__ == "__main__":
    main()
