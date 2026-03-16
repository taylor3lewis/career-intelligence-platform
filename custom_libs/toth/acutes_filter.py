#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import urllib.error
import urllib.request

import chardet

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.11 (KHTML, like Gecko) "
    "Chrome/23.0.1271.64 Safari/537.11"
)

HEADERS = {"User-Agent": USER_AGENT}


def strip_non_text(text: str) -> str:
    return re.sub(
        r"[^a-zA-ZáàãâäéèêëíìîïóòõôöúùûüçñÁÀÃÂÄÉÈÊËÍÌÎÏÓÒÕÖÔÚÙÛÜÇ\s-]",
        "",
        text,
    )


def ascii_2_portuguese(text: bytes | str) -> str:
    if isinstance(text, bytes):
        return text.decode("iso-8859-1", errors="replace")
    return text


def get_html(page: str | None = None) -> str | None:
    if page is None:
        print('Uso: get_html(page="http://www.example.com")')
        return None

    try:
        request = urllib.request.Request(page, headers=HEADERS)
        with urllib.request.urlopen(request) as response:
            content_html = response.read()

            content_type = response.headers.get("Content-Type", "")
            encoding_match = re.search(r"charset=([\w-]+)", content_type, re.IGNORECASE)
            encoding = encoding_match.group(1) if encoding_match else None

            if encoding:
                decoded = content_html.decode(encoding, errors="replace")
            else:
                raise ValueError("Charset não encontrado no header")

            # Mantém principalmente caracteres latinos, espaços e pontuação HTML básica
            html_page = re.sub(r"[^\x00-\xFF]+", "", decoded)
            return html_page

    except Exception as error_generic:
        print(f"{error_generic} (trying something else...)")

        try:
            request = urllib.request.Request(page, headers=HEADERS)
            with urllib.request.urlopen(request) as response:
                content_html = response.read()

            result = chardet.detect(content_html)
            encoding = result.get("encoding") or "utf-8"

            decoded = content_html.decode(encoding, errors="replace")
            html_page = re.sub(r"[^\x00-\xFF]+", "", decoded)
            return html_page

        except Exception as err:
            print(err)
            return None


if __name__ == "__main__":
    content = get_html("http://www.ascii.cl/htmlcodes.htm")

    if content:
        content = content.split("&#160;")[1]
        content = content.split("</table>")[0]
        content = content.replace("\r", "").replace("\n", "").replace("\t", "")
        content = re.findall(r'<TD align="center">.+?</TD>', content)

        for line in content:
            sanitized = line.replace("<br>", " ")
            sanitized = re.sub(r"<.+?>", "", sanitized)
            print(sanitized)
