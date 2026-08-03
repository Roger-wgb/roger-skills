#!/usr/bin/env python3
"""Fetch a web page and print its readable text for STORM-style source verification.

Companion to web_search.py: web_search returns candidate URLs, this opens one of
them and extracts the main text so a claim can be checked against the page's
actual wording. source-policy.md requires opening the underlying page before
citing a search snippet as fact; this script is how that happens when the
environment has no native page-fetch tool.

Only http(s) URLs are allowed. The download is size- and time-capped. Output is
plain text: a short header (title, URL, char count) followed by the extracted
body, so an agent can both read the page and record source metadata.
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

TIMEOUT_SECONDS = 20
MAX_BYTES = 5_000_000  # cap the download so a huge page can't exhaust memory
DEFAULT_MAX_CHARS = 20_000
USER_AGENT = "Mozilla/5.0 (compatible; storm-research-writer/1.0; +local-agent)"

# Tags whose content is not readable prose and should be dropped entirely.
# (Not "head": <title> lives there and is captured separately below.)
SKIP_TAGS = {"script", "style", "noscript", "template", "svg"}
# Block-level tags that should force a line break around their text.
BLOCK_TAGS = {
    "p", "div", "section", "article", "header", "footer", "li", "ul", "ol",
    "table", "tr", "br", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre",
}


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.title = ""
        self._skip_depth = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in SKIP_TAGS:
            self._skip_depth += 1
        elif tag == "title":
            self._in_title = True
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        elif tag == "title":
            self._in_title = False
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._in_title:
            self.title += data
            return
        text = data.strip()
        if text:
            self.parts.append(text + " ")

    def text(self) -> str:
        raw = "".join(self.parts)
        out: list[str] = []
        for line in raw.splitlines():
            stripped = line.strip()
            if stripped:
                out.append(stripped)
            elif out and out[-1] != "":
                out.append("")  # collapse runs of blank lines to one
        return "\n".join(out).strip()


def fetch(url: str) -> tuple[str, str]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise SystemExit(f"Refusing non-http(s) URL: {url}")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        raw = response.read(MAX_BYTES)
        charset = response.headers.get_content_charset() or "utf-8"
    html = raw.decode(charset, errors="replace")
    parser = _TextExtractor()
    parser.feed(html)
    return parser.title.strip(), parser.text()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Fetch a web page as readable text for source verification."
    )
    ap.add_argument("url", help="http(s) URL to fetch")
    ap.add_argument(
        "-n",
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help=f"Truncate the body to this many characters (default {DEFAULT_MAX_CHARS})",
    )
    args = ap.parse_args()

    try:
        title, body = fetch(args.url)
    except urllib.error.HTTPError as exc:
        print(f"fetch failed: HTTP {exc.code}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"fetch failed: {exc.reason}", file=sys.stderr)
        return 1

    truncated = len(body) > args.max_chars
    if truncated:
        body = body[: args.max_chars]

    print(f"# Title: {title or '(none)'}")
    print(f"# URL: {args.url}")
    print(f"# Chars: {len(body)}{' (truncated)' if truncated else ''}")
    print()
    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
