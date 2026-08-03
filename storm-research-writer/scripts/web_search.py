#!/usr/bin/env python3
"""Fallback web search adapter for STORM-style research.

Queries a search API and prints normalized candidate sources as JSON so an
agent can run the STORM workflow when no native web-search tool is available.

Providers (auto-selected by which env var is set, or forced with --provider):
  - brave    -> BRAVE_SEARCH_API_KEY
  - tavily   -> TAVILY_API_KEY
  - serpapi  -> SERPAPI_API_KEY

The API key is read only from the environment. It is never printed, logged,
or included in error messages or the JSON output.

Output: JSON array of objects, each with:
  title, url, snippet, source (publisher hostname), published_date

Results are CANDIDATE sources only. Do not treat a snippet as a verified
fact — open the original page or a reliable summary before citing it.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

PROVIDER_ENV = {
    "brave": "BRAVE_SEARCH_API_KEY",
    "tavily": "TAVILY_API_KEY",
    "serpapi": "SERPAPI_API_KEY",
}

# Provider-specific max result counts (per each provider's API docs).
PROVIDER_MAX_COUNT = {
    "brave": 20,
    "tavily": 20,
    "serpapi": 100,
}

TIMEOUT_SECONDS = 20

# A plain hostname: letters/digits/hyphens in each label, dot-separated, no
# scheme, path, or query operators. Rejects spaces, quotes, parentheses, "OR".
HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)


def _validate_domains(domains: list[str]) -> list[str]:
    """Reject anything that is not a bare hostname before it reaches a
    site: filter, so a stray string cannot rewrite the query semantics."""
    for domain in domains:
        if not HOSTNAME_RE.match(domain):
            raise SystemExit(
                f"Invalid domain '{domain}': expected a bare hostname like example.com"
            )
    return domains


def _hostname(url: str) -> str:
    try:
        return urllib.parse.urlparse(url).hostname or ""
    except ValueError:
        return ""


def _http_json(request: urllib.request.Request) -> Any:
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def _apply_site_filter(query: str, domains: list[str]) -> str:
    """Append site: operators so providers without a native domain filter
    (brave, serpapi) still restrict results."""
    if not domains:
        return query
    clause = " OR ".join(f"site:{d}" for d in domains)
    return f"{query} ({clause})"


def search_brave(query: str, count: int, domains: list[str], key: str) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({"q": _apply_site_filter(query, domains), "count": count})
    request = urllib.request.Request(
        f"https://api.search.brave.com/res/v1/web/search?{params}",
        headers={"Accept": "application/json", "X-Subscription-Token": key},
    )
    data = _http_json(request)
    results = []
    for item in (data.get("web", {}).get("results") or [])[:count]:
        url = item.get("url", "")
        results.append(
            {
                "title": item.get("title", ""),
                "url": url,
                "snippet": item.get("description", ""),
                "source": _hostname(url),
                "published_date": item.get("page_age") or item.get("age") or None,
            }
        )
    return results


def search_tavily(query: str, count: int, domains: list[str], key: str) -> list[dict[str, Any]]:
    body: dict[str, Any] = {"api_key": key, "query": query, "max_results": count}
    if domains:
        body["include_domains"] = domains
    request = urllib.request.Request(
        "https://api.tavily.com/search",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    data = _http_json(request)
    results = []
    for item in (data.get("results") or [])[:count]:
        url = item.get("url", "")
        results.append(
            {
                "title": item.get("title", ""),
                "url": url,
                "snippet": item.get("content", ""),
                "source": _hostname(url),
                "published_date": item.get("published_date") or None,
            }
        )
    return results


def search_serpapi(query: str, count: int, domains: list[str], key: str) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode(
        {
            "engine": "google",
            "q": _apply_site_filter(query, domains),
            "num": count,
            "api_key": key,
        }
    )
    request = urllib.request.Request(f"https://serpapi.com/search.json?{params}")
    data = _http_json(request)
    results = []
    for item in (data.get("organic_results") or [])[:count]:
        url = item.get("link", "")
        results.append(
            {
                "title": item.get("title", ""),
                "url": url,
                "snippet": item.get("snippet", ""),
                "source": _hostname(url),
                "published_date": item.get("date") or None,
            }
        )
    return results


PROVIDERS = {
    "brave": search_brave,
    "tavily": search_tavily,
    "serpapi": search_serpapi,
}


def resolve_provider(requested: str | None) -> str:
    """Pick a provider: honor the explicit choice, else the first whose key is set."""
    if requested:
        if not os.environ.get(PROVIDER_ENV[requested]):
            raise SystemExit(
                f"Provider '{requested}' selected but {PROVIDER_ENV[requested]} is not set."
            )
        return requested
    for name, env in PROVIDER_ENV.items():
        if os.environ.get(env):
            return name
    raise SystemExit(
        "No search API key found. Set one of: " + ", ".join(PROVIDER_ENV.values())
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch candidate web sources for STORM research via a search API."
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=5,
        help="Number of results (default 5; clamped to the provider max: brave/tavily 20, serpapi 100)",
    )
    parser.add_argument(
        "-d",
        "--domain",
        action="append",
        default=[],
        metavar="DOMAIN",
        help="Restrict to a domain (repeatable), e.g. -d nature.com -d who.int",
    )
    parser.add_argument(
        "-p",
        "--provider",
        choices=sorted(PROVIDERS),
        help="Force a provider (default: first one whose API key env var is set)",
    )
    args = parser.parse_args()

    provider = resolve_provider(args.provider)
    key = os.environ[PROVIDER_ENV[provider]]
    domains = _validate_domains(args.domain)
    count = max(1, min(args.count, PROVIDER_MAX_COUNT[provider]))

    try:
        results = PROVIDERS[provider](args.query, count, domains, key)
    except urllib.error.HTTPError as exc:
        # Never surface the request (it carries the key) — only the status.
        print(f"{provider} search failed: HTTP {exc.code}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"{provider} search failed: {exc.reason}", file=sys.stderr)
        return 1

    json.dump(results, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
