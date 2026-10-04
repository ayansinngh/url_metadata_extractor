"""Simple utility to fetch a web page and extract metadata."""

from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

def normalize_url(url):
    """Ensure the URL has a scheme (defaults to https)."""
    url = (url or "").strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def is_valid_url(url):
    """Check if the URL is well-formed."""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False

def extract_metadata(url):
    """Fetch the page and extract metadata."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 MetadataExtractor/1.0"
        )
    }
    
    # Download the page
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    # Parse the HTML
    try:
        soup = BeautifulSoup(response.content, "lxml")
    except Exception:
        soup = BeautifulSoup(response.content, "html.parser")
        
    parsed_url = urlparse(response.url)
    domain = parsed_url.netloc
    
    # Extract basic info
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    
    def get_meta(name_or_prop):
        tag = soup.find("meta", attrs={"name": name_or_prop}) or soup.find("meta", attrs={"property": name_or_prop})
        return tag["content"].strip() if tag and tag.get("content") else ""

    description = get_meta("description") or get_meta("og:description")
    author = get_meta("author")
    keywords = get_meta("keywords")
    
    html_tag = soup.find("html")
    language = html_tag.get("lang") if html_tag else ""
    
    # Favicon
    favicon = ""
    icon_link = soup.find("link", rel=lambda r: r and "icon" in str(r).lower())
    if icon_link and icon_link.get("href"):
        favicon = urljoin(response.url, icon_link["href"])
    else:
        favicon = urljoin(response.url, "/favicon.ico")
        
    # Open Graph & Twitter Cards
    open_graph = {}
    twitter = {}
    for meta in soup.find_all("meta"):
        prop = meta.get("property", "")
        name = meta.get("name", "")
        content = meta.get("content", "")
        
        if prop.startswith("og:") and content:
            if prop == "og:image":
                content = urljoin(response.url, content)
            open_graph[prop] = content
            
        if name.startswith("twitter:") and content:
            if name in ("twitter:image", "twitter:image:src"):
                content = urljoin(response.url, content)
            twitter[name] = content

    # Headings
    h1s = [h.get_text(strip=True) for h in soup.find_all("h1") if h.get_text(strip=True)]
    h2s = [h.get_text(strip=True) for h in soup.find_all("h2") if h.get_text(strip=True)]
    
    # Links
    internal_links = 0
    external_links = 0
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        link_domain = urlparse(urljoin(response.url, href)).netloc
        if link_domain == domain or not link_domain:
            internal_links += 1
        else:
            external_links += 1
            
    # Check for JS-rendered pages
    scripts = len(soup.find_all("script"))
    text_length = len(soup.get_text(strip=True))
    notice = ""
    if text_length < 300 and scripts >= 3:
        notice = "Page looks JavaScript-rendered; metadata may be incomplete."

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