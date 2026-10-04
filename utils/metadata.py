
"""Utilities for fetching a webpage and extracting its metadata."""

from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def normalize_url(url):
    """Add https:// when the user does not provide a URL scheme."""
    url = (url or "").strip()

    if not url:
        return ""

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    return url


def is_valid_url(url):
    """Check whether the URL contains a scheme and domain."""
    try:
        parsed_url = urlparse(url)

        return bool(
            parsed_url.scheme in ("http", "https")
            and parsed_url.netloc
        )

    except ValueError:
        return False


def extract_metadata(url):
    """Fetch a webpage and extract useful metadata from its HTML."""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }

    # Fetch the webpage.
    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    # Parse the HTML.
    try:
        soup = BeautifulSoup(response.content, "lxml")
    except Exception:
        soup = BeautifulSoup(response.content, "html.parser")

    # Get the final URL after redirects.
    parsed_url = urlparse(response.url)
    domain = parsed_url.netloc

    # --------------------------------
    # Basic metadata
    # --------------------------------

    title = ""

    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    def get_meta(name_or_property):
        """Find a meta tag using either name or property."""
        tag = soup.find(
            "meta",
            attrs={"name": name_or_property}
        )

        if not tag:
            tag = soup.find(
                "meta",
                attrs={"property": name_or_property}
            )

        if tag and tag.get("content"):
            return tag["content"].strip()

        return ""

    description = (
        get_meta("description")
        or get_meta("og:description")
    )

    author = get_meta("author")
    keywords = get_meta("keywords")

    # HTML language.
    html_tag = soup.find("html")
    language = ""

    if html_tag:
        language = html_tag.get("lang", "")

    # --------------------------------
    # Favicon
    # --------------------------------

    favicon = ""

    icon_link = soup.find(
        "link",
        rel=lambda value: (
            value and "icon" in str(value).lower()
        )
    )

    if icon_link and icon_link.get("href"):
        favicon = urljoin(
            response.url,
            icon_link["href"]
        )
    else:
        favicon = urljoin(
            response.url,
            "/favicon.ico"
        )

    # --------------------------------
    # Open Graph and Twitter metadata
    # --------------------------------

    open_graph = {}
    twitter = {}

    for meta in soup.find_all("meta"):

        property_name = meta.get("property", "")
        meta_name = meta.get("name", "")
        content = meta.get("content", "").strip()

        if not content:
            continue

        # Open Graph tags.
        if property_name.startswith("og:"):

            if property_name == "og:image":
                content = urljoin(
                    response.url,
                    content
                )

            open_graph[property_name] = content

        # Twitter card tags.
        if meta_name.startswith("twitter:"):

            if meta_name in (
                "twitter:image",
                "twitter:image:src"
            ):
                content = urljoin(
                    response.url,
                    content
                )

            twitter[meta_name] = content

    # --------------------------------
    # Headings
    # --------------------------------

    h1s = [
        heading.get_text(" ", strip=True)
        for heading in soup.find_all("h1")
        if heading.get_text(" ", strip=True)
    ]

    h2s = [
        heading.get_text(" ", strip=True)
        for heading in soup.find_all("h2")
        if heading.get_text(" ", strip=True)
    ]

    # --------------------------------
    # Links
    # --------------------------------

    internal_links = 0
    external_links = 0

    for link in soup.find_all("a", href=True):

        href = link["href"].strip()

        # Ignore non-page links.
        if href.startswith((
            "#",
            "javascript:",
            "mailto:",
            "tel:"
        )):
            continue

        absolute_url = urljoin(
            response.url,
            href
        )

        link_domain = urlparse(
            absolute_url
        ).netloc

        if link_domain == domain:
            internal_links += 1
        else:
            external_links += 1

    # --------------------------------
    # JavaScript-rendered page check
    # --------------------------------

    scripts = len(soup.find_all("script"))

    text_length = len(
        soup.get_text(" ", strip=True)
    )

    notice = ""

    if text_length < 300 and scripts >= 3:
        notice = (
            "This page may be JavaScript-rendered, "
            "so some metadata may be incomplete."
        )

    # --------------------------------
    # Return extracted data
    # --------------------------------

    return {
        "url": response.url,
        "domain": domain,
        "title": title,
        "description": description,
        "language": language,
        "author": author,
        "keywords": keywords,
        "favicon": favicon,

        "open_graph": open_graph,
        "twitter": twitter,

        "headings": {
            "h1": h1s[:5],
            "h2": h2s[:5]
        },

        "links": {
            "total": internal_links + external_links,
            "internal": internal_links,
            "external": external_links
        },

        "notice": notice
    }

