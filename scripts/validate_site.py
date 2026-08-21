#!/usr/bin/env python3
"""Validate the static site contract used by CI."""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
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
        self.canonical_count = 0
        self.meta: dict[str, str] = {}
        self.open_graph: dict[str, str] = {}
        self.twitter: dict[str, str] = {}
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
        elif tag == "meta":
            name = (attributes.get("name") or "").lower()
            property_name = (attributes.get("property") or "").lower()
            content = attributes.get("content") or ""
            if name:
                self.meta[name] = content
            if property_name.startswith("og:"):
                self.open_graph[property_name] = content
            if name.startswith("twitter:"):
                self.twitter[name] = content
        elif tag == "link" and "canonical" in (attributes.get("rel", "") or "").lower():
            self.canonical_count += 1
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
        if parser.canonical_count != 1:
            errors.append(f"expected exactly one canonical link, got {parser.canonical_count}")
        expected_title = "2BRAIN — ИИ-трансформация и продуктовая разработка"
        expected_description = "2BRAIN помогает компаниям находить перспективные ИИ-сценарии, запускать продукты и масштабировать работающие решения."
        if parser.title != expected_title:
            errors.append("title changed without an approved copy update")
        if parser.description != expected_description:
            errors.append("meta description changed without an approved copy update")
        if parser.h1_count != 1:
            errors.append(f"expected exactly one H1, got {parser.h1_count}")
        for asset in parser.local_assets:
            if asset and not (site / asset).is_file():
                errors.append(f"local asset is missing: {asset}")

        html = index.read_text(encoding="utf-8")
        if 'type="application/ld+json"' not in html or '"@type": "Organization"' not in html:
            errors.append("Organization JSON-LD is missing")
        else:
            try:
                blocks = []
                marker = '<script type="application/ld+json">'
                for block in html.split(marker)[1:]:
                    blocks.append(block.split("</script>", 1)[0].strip())
                structured = [json.loads(block) for block in blocks]
                graph = [item for data in structured for item in data.get("@graph", [])]
                types = {item.get("@type") for item in graph}
                required_types = {"Organization", "Person", "WebSite", "WebPage", "Service", "ItemList"}
                missing_types = required_types - types
                if missing_types:
                    errors.append(f"JSON-LD types are missing: {', '.join(sorted(missing_types))}")
                product_urls = {item.get("item", {}).get("url") for item in next((item for item in graph if item.get("@type") == "ItemList"), {}).get("itemListElement", [])}
                expected_product_urls = {"https://airis.you/", "https://rec.2brain.pro/", "https://ykai.tilda.ws/astra", "https://tutor.2brain.pro/"}
                if product_urls != expected_product_urls:
                    errors.append("JSON-LD product URLs do not match the crawlable product links")
            except (ValueError, TypeError, KeyError, IndexError) as exc:
                errors.append(f"JSON-LD is invalid: {exc}")

        required_meta = {
            "og:type": "website",
            "og:locale": "ru_RU",
            "og:site_name": "2BRAIN",
            "og:url": "https://2brain.pro/",
            "og:image:type": "image/png",
            "og:image:width": "560",
            "og:image:height": "560",
            "twitter:card": "summary_large_image",
            "twitter:image": "https://2brain.pro/assets/images/yan-shishenya-editorial-v4-square.png",
        }
        for key, expected in required_meta.items():
            actual = parser.open_graph.get(key) if key.startswith("og:") else parser.meta.get(key)
            if actual != expected:
                errors.append(f"{key} must be {expected!r}, got {actual!r}")

    robots = site / "robots.txt"
    sitemap = site / "sitemap.xml"
    if not robots.is_file() or "Sitemap: https://2brain.pro/sitemap.xml" not in robots.read_text(encoding="utf-8"):
        errors.append("robots.txt is missing or does not reference the canonical sitemap")
    if not sitemap.is_file() or "https://2brain.pro/" not in sitemap.read_text(encoding="utf-8"):
        errors.append("sitemap.xml is missing or does not contain the canonical homepage")
    elif sitemap.is_file():
        try:
            root_element = ET.parse(sitemap).getroot()
            locs = [element.text for element in root_element.iter() if element.tag.endswith("}loc")]
            if locs != ["https://2brain.pro/"]:
                errors.append("sitemap.xml must contain only the canonical homepage")
        except ET.ParseError as exc:
            errors.append(f"sitemap.xml is invalid XML: {exc}")

    llms = site / "llms.txt"
    if not llms.is_file() or "https://2brain.pro/" not in llms.read_text(encoding="utf-8"):
        errors.append("llms.txt is missing or does not reference the homepage")

    result = {"ok": not errors, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
