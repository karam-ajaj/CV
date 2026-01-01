#!/usr/bin/env python3
"""Generate sitemap.xml for cv.vnerd.nl.

- Includes main pages and PDF assets under resrc/
- Excludes temporary/low-value folders to keep the sitemap focused
- Writes sitemap.xml in the repository root
"""

from __future__ import annotations

import datetime as dt
import os
import urllib.parse
from pathlib import Path

BASE_URL = "https://cv.vnerd.nl/"
ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"

# Explicitly list HTML pages we want indexed.
HTML_PAGES = [
    ("", ROOT / "index.html", 1.0, "weekly"),
    ("badges.html", ROOT / "badges.html", 0.7, "monthly"),
]

# Folder prefixes (relative to repo root) to skip.
EXCLUDE_PREFIXES = [
    "resrc/Temp/",  # transient or acknowledgement artifacts
]


def should_exclude(rel_path: str) -> bool:
    return any(rel_path.startswith(prefix) for prefix in EXCLUDE_PREFIXES)


def isoformat_mtime(path: Path) -> str:
    mtime = dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc)
    return mtime.isoformat(timespec="seconds")


def iter_pdf_entries():
    for path in ROOT.joinpath("resrc").rglob("*.pdf"):
        rel_path = path.relative_to(ROOT).as_posix()
        if should_exclude(f"{rel_path}/") or should_exclude(rel_path):
            continue
        yield (
            rel_path,
            isoformat_mtime(path),
            0.5,
            "yearly",
        )


def encode_url(rel_path: str) -> str:
    return urllib.parse.urljoin(BASE_URL, urllib.parse.quote(rel_path, safe="/"))


def build_entries():
    entries = []
    for rel_path, abs_path, priority, changefreq in HTML_PAGES:
        entries.append(
            (encode_url(rel_path), isoformat_mtime(abs_path), priority, changefreq)
        )
    for rel_path, lastmod, priority, changefreq in iter_pdf_entries():
        entries.append((encode_url(rel_path), lastmod, priority, changefreq))
    entries.sort(key=lambda item: item[0])
    return entries


def to_xml(entries):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, lastmod, priority, changefreq in entries:
        lines.extend(
            [
                "  <url>",
                f"    <loc>{loc}</loc>",
                f"    <lastmod>{lastmod}</lastmod>",
                f"    <changefreq>{changefreq}</changefreq>",
                f"    <priority>{priority:.1f}</priority>",
                "  </url>",
            ]
        )
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main() -> None:
    entries = build_entries()
    SITEMAP.write_text(to_xml(entries), encoding="utf-8")
    print(f"Wrote {len(entries)} entries to {SITEMAP}")


if __name__ == "__main__":
    main()
