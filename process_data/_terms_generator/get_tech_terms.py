# -*- coding: utf-8 -*-

import re
from pathlib import Path
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
from nltk.corpus import stopwords, words
from unidecode import unidecode

from custom_libs.toth.toth import check_term_integrity
from wiki_links import LINKS

sw_english = {k: None for k in words.words()}

STOP_WORDS = set(stopwords.words("portuguese")) | set(stopwords.words("english"))
LOCAL_STOP_FRAGMENT = {"wiki"}

ACCEPTED: set[str] = set()
REJECTED: set[str] = set()


def build_file_name(link: str) -> str:
    last_part = unquote(link).split("/")[-1].lower()
    return re.sub(r"[^a-z0-9_]", "", unidecode(last_part))


def fetch_content(link: str):
    response = requests.get(link, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "lxml")
    return soup.find("div", {"id": "mw-content-text"})


def clean_content(content) -> None:
    selectors = [
        ("div", {"class": "reflist"}),
        ("div", {"class": "toc"}),
        ("h2", {}),
        ("table", {"class": "nowraplinks"}),
        ("ul", {"class": "noprint"}),
        ("a", {"class": "mw-redirect"}),
        ("a", {"class": "external text"}),
        ("sup", {}),
        ("span", {}),
    ]

    for tag_name, attrs in selectors:
        for element in content.find_all(tag_name, attrs):
            element.extract()


def normalize_term(term: str) -> str:
    term = re.sub(r"(\[.+?])", "", term)
    term = re.sub(r"(\(.+?\))", "", term)
    term = re.sub(r"[()]", "", term)
    return term.strip()


def is_valid_fragment(frag: str) -> bool:
    frag = frag.strip()

    if not frag:
        return False

    if re.match(r"((www\..+?\.(com|pt|br))|(https?://)?[-a-z0-9.]+?/)", frag):
        return False

    if re.match(r".*?[^0-9.]+?.*?", frag) is None:
        return False

    if re.match(r"[a-zA-Z]+?", frag) is None:
        return False

    if not check_term_integrity(frag):
        return False

    if any(fragment in frag.lower() for fragment in LOCAL_STOP_FRAGMENT):
        return False

    if frag in STOP_WORDS:
        return False

    return True


def extract_terms_from_content(content) -> None:
    for item in content.find_all("a"):
        text = item.get_text(strip=True)

        if not text or text.startswith("http://") or "[" in text:
            continue

        for term in text.split():
            cleaned_term = normalize_term(term)

            for frag in cleaned_term.split():
                frag = frag.strip()
                if not frag:
                    continue

                if is_valid_fragment(frag):
                    ACCEPTED.add(frag)
                else:
                    REJECTED.add(frag)


def save_terms(path: str | Path, terms: set[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for term in sorted(terms):
            f.write(term + "\n")


def main() -> None:
    for link in LINKS:
        file_name = build_file_name(link)
        print(file_name)

        content = fetch_content(link)
        if content is None:
            print(f"Could not find content div for: {link}")
            continue

        clean_content(content)
        extract_terms_from_content(content)

    save_terms("ACCEPTED.txt", ACCEPTED)
    save_terms("REJECTED.txt", REJECTED)


if __name__ == "__main__":
    main()
