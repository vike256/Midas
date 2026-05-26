"""
Midas — core build logic.
"""

import copy
import http.server
import os
import re
import shutil
import socketserver
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import markdown
import yaml
from importlib.resources import files
from jinja2 import ChoiceLoader, Environment, FileSystemLoader, select_autoescape

# ---------------------------------------------------------------------------
# Paths (relative to cwd where the command is run)
# ---------------------------------------------------------------------------

CONTENT_DIR = Path("site")
PROJECT_TEMPLATES_DIR = Path("templates")
DIST_DIR = Path("_dist")

# Package paths (for built-in templates and CSS)
PACKAGE_DIR = files("midas")
PACKAGE_TEMPLATES_DIR = PACKAGE_DIR / "templates"
PACKAGE_STATIC_DIR = PACKAGE_DIR / "static"
ICONS_DIR = PROJECT_TEMPLATES_DIR / "icons"

# ---------------------------------------------------------------------------
# Content parsing
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_markdown_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")

    frontmatter = {}
    body = text
    match = FRONTMATTER_RE.match(text)
    if match:
        frontmatter = yaml.safe_load(match.group(1)) or {}
        body = text[match.end():]

    return {
        "path": path,
        "frontmatter": frontmatter,
        "body": body,
    }


def classify_page(path: Path, frontmatter: dict) -> str:
    if frontmatter.get("type"):
        return frontmatter["type"]
    if path.name.lower() == "index.md":
        return "home"
    return "page"


def assign_collection(path: Path, config: dict) -> str | None:
    collections = config.get("collections", {})
    if not collections:
        return None
    rel = path.relative_to(CONTENT_DIR)
    parts = rel.parts
    if len(parts) > 1:
        name = parts[0]
        if name in collections:
            return name
    return None


def extract_date(path: Path, frontmatter: dict) -> str | None:
    if "date" in frontmatter:
        return str(frontmatter["date"])
    return None


def generate_slug(path: Path) -> str:
    return path.stem.lower().replace(" ", "-")


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def make_markdown() -> markdown.Markdown:
    return markdown.Markdown(
        tab_length=2,
        extensions=[
            "fenced_code",
            "tables",
            "toc",
            "md_in_html",
            "codehilite",
            "attr_list",
        ],
        extension_configs={
            "codehilite": {
                "css_class": "highlight",
                "use_pygments": True,
                "noclasses": False,
            },
        },
    )


def render_markdown(body: str) -> str:
    body = re.sub(r"~~(.+?)~~", r"<del>\1</del>", body)
    md = make_markdown()
    return md.convert(body)


def _add_external_link_attrs(html: str, site_url: str) -> str:
    if not site_url:
        return html
    site_url = site_url.rstrip("/")

    def _process_tag(match):
        tag = match.group(0)
        href_match = re.search(r'href=["\']([^"\']+)["\']', tag)
        if not href_match:
            return tag
        href = href_match.group(1)
        if not href.startswith(("http://", "https://")):
            return tag
        if href.startswith(site_url):
            return tag

        additions = []
        if "target=" not in tag:
            additions.append('target="_blank"')
        if "rel=" not in tag:
            additions.append('rel="noopener noreferrer"')

        if additions:
            tag = tag[:-1] + " " + " ".join(additions) + ">"

        return tag

    return re.sub(r'<a\b[^>]*>', _process_tag, html)


# ---------------------------------------------------------------------------
# RSS
# ---------------------------------------------------------------------------

def build_rss(
    config: dict,
    posts: list[dict],
    output_path: Path,
    language: str | None = None,
) -> None:
    site_url = config["site"]["url"].rstrip("/")
    site_name = config["site"]["name"]
    site_desc = config["site"].get("description", "")

    feed_url = f"{site_url}/{output_path.relative_to(DIST_DIR).as_posix()}"
    link_url = site_url

    rss = ET.Element("rss", version="2.0", attrib={"xmlns:media": "http://search.yahoo.com/mrss/"})
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = site_name
    ET.SubElement(channel, "link").text = link_url
    ET.SubElement(channel, "description").text = site_desc
    if language:
        ET.SubElement(channel, "language").text = language
    ET.SubElement(channel, "lastBuildDate").text = _rfc822_date(datetime.now(timezone.utc))
    ET.SubElement(channel, "generator").text = "Midas"

    for post in posts[:20]:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = post.get("title", post["slug"])
        ET.SubElement(item, "link").text = f"{site_url}{post['url']}"
        ET.SubElement(item, "guid", isPermaLink="true").text = f"{site_url}{post['url']}"
        if post.get("date"):
            ET.SubElement(item, "pubDate").text = _rfc822_date(post["date"])
        if post.get("description"):
            ET.SubElement(item, "description").text = post["description"]
        cover = post.get("coverImage", "")
        if cover:
            if not cover.startswith("http"):
                cover = site_url + "/" + cover.lstrip("/")
            ET.SubElement(item, "{http://search.yahoo.com/mrss/}thumbnail", url=cover)

    tree = ET.ElementTree(rss)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)


def _rfc822_date(value) -> str:
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            value = datetime.now(timezone.utc)
    if isinstance(value, datetime):
        return value.strftime("%a, %d %b %Y %H:%M:%S %z")
    return ""


# ---------------------------------------------------------------------------
# Icons
# ---------------------------------------------------------------------------

def load_icons() -> dict[str, str]:
    icons = {}
    builtin_icons_dir = PACKAGE_TEMPLATES_DIR / "icons"
    if builtin_icons_dir.exists():
        for svg_path in builtin_icons_dir.glob("*.svg"):
            icons[svg_path.stem] = svg_path.read_text(encoding="utf-8")
    if ICONS_DIR.exists():
        for svg_path in ICONS_DIR.glob("*.svg"):
            icons[svg_path.stem] = svg_path.read_text(encoding="utf-8")
    return icons


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build(config: dict) -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    default_lang = config["site"].get("default_language", "en")
    collections_cfg = config.get("collections", {})

    # ------------------------------------------------------------------
    # 1. Parse all markdown files
    # ------------------------------------------------------------------
    pages = []
    if CONTENT_DIR.exists():
        for md_path in sorted(CONTENT_DIR.rglob("*.md")):
            parsed = parse_markdown_file(md_path)
            fm = parsed["frontmatter"]
            body = parsed["body"]

            page_type = classify_page(md_path, fm)
            slug = generate_slug(md_path)
            date = extract_date(md_path, fm)

            # Assign collection for posts
            collection_name = None
            if page_type == "post":
                collection_name = assign_collection(md_path, config)

            # Language
            if page_type == "post" and collection_name:
                coll_cfg = collections_cfg.get(collection_name, {})
                lang = fm.get("language") or coll_cfg.get("language") or default_lang
            else:
                lang = fm.get("language") or default_lang

            # URL
            if page_type == "home":
                url = "/"
                output_file = DIST_DIR / "index.html"
            elif page_type == "post" and collection_name:
                url = f"/{collection_name}/{slug}/"
                output_file = DIST_DIR / collection_name / slug / "index.html"
            else:
                if slug == "404":
                    url = "/404.html"
                    output_file = DIST_DIR / "404.html"
                else:
                    url = f"/{slug}/"
                    output_file = DIST_DIR / slug / "index.html"

            pages.append({
                "path": md_path,
                "type": page_type,
                "language": lang,
                "date": date,
                "slug": slug,
                "collection": collection_name,
                "title": fm.get("title", "" if page_type == "home" else slug.replace("-", " ").title()),
                "description": fm.get("description", ""),
                "coverImage": fm.get("coverImage", ""),
                "frontmatter": fm,
                "body": body,
                "url": url,
                "output_file": output_file,
            })

    # ------------------------------------------------------------------
    # 2. Group posts by collection
    # ------------------------------------------------------------------
    collections_data: dict[str, dict] = {}
    for coll_name in collections_cfg:
        coll_posts = [p for p in pages if p["type"] == "post" and p["collection"] == coll_name]
        for p in coll_posts:
            p["date_obj"] = _parse_date(p["date"])
        coll_posts.sort(key=lambda p: p["date_obj"] or datetime.min, reverse=True)
        coll_cfg = collections_cfg.get(coll_name, {})
        collections_data[coll_name] = {
            "name": coll_name,
            "title": coll_cfg.get("title", coll_name.title()),
            "language": coll_cfg.get("language"),
            "feed": coll_cfg.get("feed"),
            "posts": coll_posts,
        }

    # ------------------------------------------------------------------
    # 3. Prepare Jinja2
    # ------------------------------------------------------------------
    loaders = []
    overridden = []
    if PROJECT_TEMPLATES_DIR.exists():
        loaders.append(FileSystemLoader(str(PROJECT_TEMPLATES_DIR)))
        overridden = [f.name for f in PROJECT_TEMPLATES_DIR.glob("*.html")]
    loaders.append(FileSystemLoader(str(PACKAGE_TEMPLATES_DIR)))

    env = Environment(
        loader=ChoiceLoader(loaders),
        autoescape=select_autoescape(["html", "xml"]),
    )

    icons = load_icons()

    def icon_filter(name: str) -> str:
        return icons.get(name, "")

    env.filters["icon"] = icon_filter

    # ------------------------------------------------------------------
    # 4. Render pages
    # ------------------------------------------------------------------
    for page in pages:
        template_map = {"home": "home.html", "post": "post.html", "page": "page.html"}
        template_name = template_map.get(page["type"], "page.html")
        if PROJECT_TEMPLATES_DIR.exists() and (PROJECT_TEMPLATES_DIR / template_name).exists():
            pass
        elif not (PACKAGE_TEMPLATES_DIR / template_name).exists():
            template_name = "page.html"

        template = env.get_template(template_name)

        # Recent posts for this page
        coll = collections_data.get(page["collection"]) if page["type"] == "post" and page["collection"] else None
        recent = coll["posts"][:config.get("recentPosts", 3)] if coll else []

        # Home data
        home_data = config.get("home", {})
        if page["type"] == "home" and page["frontmatter"]:
            home_data = {**home_data, **page["frontmatter"]}

        # Auto-detect profile picture if not explicitly set
        if not home_data.get("profilePic"):
            img_dir = CONTENT_DIR / "img"
            for ext in (".png", ".jpg", ".jpeg", ".webp"):
                candidate = img_dir / f"profile{ext}"
                if candidate.exists():
                    home_data = {**home_data, "profilePic": f"/img/profile{ext}"}
                    break

        html = template.render(
            site=config["site"],
            page=page,
            content=render_markdown(page["body"]),
            collections=collections_data,
            collection=coll,
            posts=coll["posts"] if coll else [],
            home=home_data,
            icons=icons,
            config=config,
        )

        html = _add_external_link_attrs(html, config["site"].get("url", ""))

        page["output_file"].parent.mkdir(parents=True, exist_ok=True)
        page["output_file"].write_text(html, encoding="utf-8")

    # ------------------------------------------------------------------
    # 5. Render collection listing pages
    # ------------------------------------------------------------------
    for coll_name, coll_data in collections_data.items():
        posts = coll_data["posts"]
        if not posts:
            continue

        list_url = f"/{coll_name}/"
        list_output = DIST_DIR / coll_name / "index.html"

        template = env.get_template("post-list.html")
        html = template.render(
            site=config["site"],
            page={"title": coll_data["title"], "url": list_url, "language": coll_data.get("language") or default_lang},
            collection=coll_data,
            posts=posts,
            collections=collections_data,
            home=config.get("home", {}),
            icons=icons,
            config=config,
        )

        html = _add_external_link_attrs(html, config["site"].get("url", ""))

        list_output.parent.mkdir(parents=True, exist_ok=True)
        list_output.write_text(html, encoding="utf-8")

    # ------------------------------------------------------------------
    # 6. RSS feeds — grouped by feed path
    # ------------------------------------------------------------------
    if config["site"].get("url"):
        feeds: dict[str, dict] = {}
        for coll_data in collections_data.values():
            feed_path = coll_data.get("feed")
            if not feed_path:
                continue
            if feed_path not in feeds:
                feeds[feed_path] = {"posts": [], "language": None}
            feeds[feed_path]["posts"].extend(coll_data["posts"])
            if feeds[feed_path]["language"] is None and coll_data.get("language"):
                feeds[feed_path]["language"] = coll_data["language"]

        for feed_path, feed_data in feeds.items():
            feed_data["posts"].sort(key=lambda p: p["date_obj"] or datetime.min, reverse=True)
            feed_output = DIST_DIR / feed_path.lstrip("/")
            build_rss(config, feed_data["posts"], feed_output, feed_data["language"])

    # ------------------------------------------------------------------
    # 7. Copy CSS and static assets
    # ------------------------------------------------------------------
    package_css = PACKAGE_STATIC_DIR / "style.css"
    if package_css.exists():
        shutil.copy2(package_css, DIST_DIR / "midas.css")

    if CONTENT_DIR.exists():
        for src in CONTENT_DIR.rglob("*"):
            if src.is_file() and src.suffix.lower() != ".md":
                dst = DIST_DIR / src.relative_to(CONTENT_DIR)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

    if overridden:
        print(f"Templates overridden: {', '.join(overridden)}")
        print("These will not receive updates from Midas automatically.")

    print(f"Build complete: {DIST_DIR}")


def _parse_date(value) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None
    return None


# ---------------------------------------------------------------------------
# Serve
# ---------------------------------------------------------------------------

class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send_error(self, code, message=None):
        if code == 404:
            try:
                with open("404.html", "rb") as f:
                    content = f.read()
                self.send_response(404)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            except FileNotFoundError:
                pass
        super().send_error(code, message)


def _bind_server(handler, start_port: int) -> tuple[socketserver.TCPServer, int]:
    port = start_port
    while True:
        try:
            httpd = socketserver.TCPServer(("", port), handler)
            return httpd, port
        except OSError as exc:
            if exc.errno != 98:
                raise
            port += 1


def serve(port: int = 8000) -> None:
    os.chdir(DIST_DIR)
    handler = _QuietHandler
    httpd, bound_port = _bind_server(handler, port)
    with httpd:
        print(f"Serving at http://localhost:{bound_port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
