# URL Metadata Extractor

A modern, fast web application built with **Flask**, **Requests**, and **BeautifulSoup4**. Enter any web address to fetch and extract titles, descriptions, favicons, Open Graph tags, Twitter Cards, H1/H2 headings, and page link counts.

## Tech Stack
- **Backend:** Python 3, Flask, Requests, BeautifulSoup4, `urllib.parse`
- **Frontend:** Semantic HTML5, Jinja2, Vanilla CSS (Modern Dark Design System)

## Project Structure
```
url-metadata-extractor/
│
├── app.py              # Flask routes, form handling, and API endpoints
├── requirements.txt    # Python dependencies
├── README.md           # Documentation
├── .gitignore          # Git exclusion rules
│
├── templates/
│   └── index.html      # Jinja2 template with responsive results card
│
├── static/
│   └── style.css       # Premium responsive dark theme styling
│
└── utils/
    └── metadata.py     # Independent fetching and metadata extraction logic
```

## Setup & Running Locally

1. **Clone or navigate to the directory**:
   ```bash
   cd url_metadata_extractor
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate       # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Flask server**:
   ```bash
   python app.py
   ```
   Open https://vercel.com/ayansinnghs-projects/url_metadata_extractor in your web browser.

## Features & What It Extracts
- **Title & Description:** Automatically prioritizes standard tags with fallback to Open Graph and Twitter Card tags.
- **Favicon Detection:** Scans for apple-touch-icon, shortcut icons, or root `/favicon.ico`.
- **Open Graph Metadata:** Complete map of all `og:*` properties and preview image rendering.
- **Twitter Card:** Complete extraction of `twitter:*` properties and previews.
- **Headings Structure:** All `h1` and `h2` headings found across the page.
- **Link Graph Counts:** Total count partitioned into internal vs. external domain links.
- **Robust Error Handling:** Detects network timeouts, connection drops, non-HTML responses, and malformed URLs.
- **API Support:** Includes an optional endpoint `/api/metadata?url=...` for headless or JSON integrations.
