#!/usr/bin/env python3
"""Validate the static site contract used by CI."""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


class SiteParser(HTMLParser):
    """Collect the small set of HTML signals that must always be present."""

    def __init__(self) -> None:
        super().__init__()
        self.lang: str | None = None
        self.title = ""
        self.description = ""
        self.canonical: str | None = None
        self.h1_count = 0
        self._in_title = False
        self._title_parts: list[str] = []
        self.local_assets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "html":
            self.lang = attributes.get("lang")
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta" and attributes.get("name", "").lower() == "description":
            self.description = attributes.get("content", "") or ""
        elif tag == "link" and "canonical" in (attributes.get("rel", "") or "").lower():
            self.canonical = attributes.get("href")

        for attribute in ("href", "src"):
            value = attributes.get(attribute)
            if value and not value.startswith(("#", "data:", "http://", "https://", "//")):
                self.local_assets.append(urlsplit(value).path.lstrip("/"))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.title = " ".join("".join(self._title_parts).split())
            self._title_parts.clear()
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    site = root / "site"
    index = site / "index.html"
    errors: list[str] = []

    if not index.is_file():
        errors.append("site/index.html is missing")
    else:
        parser = SiteParser()
        parser.feed(index.read_text(encoding="utf-8"))
        if parser.lang != "ru":
            errors.append(f"expected <html lang=\"ru\">, got {parser.lang!r}")
        if not parser.title:
            errors.append("title is missing")
        if not parser.description:
            errors.append("meta description is missing")
        if parser.canonical != "https://2brain.pro/":
            errors.append(f"canonical must be https://2brain.pro/, got {parser.canonical!r}")
        if parser.h1_count != 1:
            errors.append(f"expected exactly one H1, got {parser.h1_count}")
        for asset in parser.local_assets:
            if asset and not (site / asset).is_file():
                errors.append(f"local asset is missing: {asset}")

        html = index.read_text(encoding="utf-8")
        if 'type="application/ld+json"' not in html or '"@type": "Organization"' not in html:
            errors.append("Organization JSON-LD is missing")

    robots = site / "robots.txt"
    sitemap = site / "sitemap.xml"
    if not robots.is_file() or "Sitemap: https://2brain.pro/sitemap.xml" not in robots.read_text(encoding="utf-8"):
        errors.append("robots.txt is missing or does not reference the canonical sitemap")
    if not sitemap.is_file() or "https://2brain.pro/" not in sitemap.read_text(encoding="utf-8"):
        errors.append("sitemap.xml is missing or does not contain the canonical homepage")

    result = {"ok": not errors, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
