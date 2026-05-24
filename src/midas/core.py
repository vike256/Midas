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

CONTENT_DIR = Path("content")
PROJECT_TEMPLATES_DIR = Path("templates")
STATIC_DIR = Path("static")
DIST_DIR = Path("dist")

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


def classify_file(path: Path, frontmatter: dict, config: dict) -> str:
    if frontmatter.get("type"):
        return frontmatter["type"]
    if path.name.lower() == "index.md":
        return "home"
    post_prefix = config.get("postPrefix", "")
    if post_prefix and post_prefix in path.parts:
        return "blog"
    for lang in config["languages"].get("additional", []):
        if lang in path.parts:
            return "blog"
    if "posts" in path.parts:
        return "blog"
    return "page"


def infer_language(path: Path, config: dict) -> str:
    parts = path.parts
    for lang in config["languages"].get("additional", []):
        if lang in parts:
            return lang
    return config["languages"]["default"]


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
        extensions=[
            "fenced_code",
            "tables",
            "toc",
            "md_in_html",
            "codehilite",
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
    # Strikethrough: ~~text~~ -> <del>text</del>
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
    language: str,
    posts: list[dict],
    output_path: Path,
) -> None:
    site_url = config["site"]["url"].rstrip("/")
    site_name = config["site"]["name"]
    site_desc = config["site"].get("description", "")

    if language == config["languages"]["default"]:
        feed_url = f"{site_url}/feed.xml"
        link_url = site_url
    else:
        feed_url = f"{site_url}/{language}/feed.xml"
        link_url = f"{site_url}/{language}"

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = site_name
    ET.SubElement(channel, "link").text = link_url
    ET.SubElement(channel, "description").text = site_desc
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
    # Built-in icons shipped with the package
    builtin_icons_dir = PACKAGE_TEMPLATES_DIR / "icons"
    if builtin_icons_dir.exists():
        for svg_path in builtin_icons_dir.glob("*.svg"):
            icons[svg_path.stem] = svg_path.read_text(encoding="utf-8")
    # User project icons override built-ins
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

    # ------------------------------------------------------------------
    # 1. Parse all markdown files
    # ------------------------------------------------------------------
    pages = []
    if CONTENT_DIR.exists():
        for md_path in sorted(CONTENT_DIR.rglob("*.md")):
            parsed = parse_markdown_file(md_path)
            fm = parsed["frontmatter"]
            body = parsed["body"]

            page_type = classify_file(md_path, fm, config)
            language = fm.get("language") or infer_language(md_path, config)
            date = extract_date(md_path, fm)
            slug = generate_slug(md_path)

            # Determine URL
            if page_type == "home":
                url = "/"
                output_file = DIST_DIR / "index.html"
            elif page_type == "blog":
                if language == config["languages"]["default"]:
                    post_prefix = config.get("postPrefix", "")
                    if post_prefix:
                        url = f"/{post_prefix}/{slug}/"
                        output_file = DIST_DIR / post_prefix / slug / "index.html"
                    else:
                        url = f"/{slug}/"
                        output_file = DIST_DIR / slug / "index.html"
                else:
                    url = f"/{language}/{slug}/"
                    output_file = DIST_DIR / language / slug / "index.html"
            else:  # page
                if slug == "404" and language == config["languages"]["default"]:
                    url = "/404.html"
                    output_file = DIST_DIR / "404.html"
                elif language != config["languages"]["default"]:
                    url = f"/{language}/{slug}/"
                    output_file = DIST_DIR / language / slug / "index.html"
                else:
                    url = f"/{slug}/"
                    output_file = DIST_DIR / slug / "index.html"

            pages.append({
                "path": md_path,
                "type": page_type,
                "language": language,
                "date": date,
                "slug": slug,
                "title": fm.get("title", "" if page_type == "home" else slug.replace("-", " ").title()),
                "description": fm.get("description", ""),
                "coverImage": fm.get("coverImage", ""),
                "frontmatter": fm,
                "body": body,
                "url": url,
                "output_file": output_file,
            })

    # ------------------------------------------------------------------
    # 2. Group blog posts
    # ------------------------------------------------------------------
    blog_posts = [p for p in pages if p["type"] == "blog"]
    for post in blog_posts:
        post["date_obj"] = _parse_date(post["date"])
    blog_posts.sort(key=lambda p: p["date_obj"] or datetime.min, reverse=True)

    posts_by_language: dict[str, list[dict]] = {}
    for post in blog_posts:
        posts_by_language.setdefault(post["language"], []).append(post)

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
        template_map = {"home": "home.html", "blog": "post.html", "page": "page.html"}
        template_name = template_map.get(page["type"], "page.html")
        if PROJECT_TEMPLATES_DIR.exists() and (PROJECT_TEMPLATES_DIR / template_name).exists():
            pass  # user override wins
        elif not (PACKAGE_TEMPLATES_DIR / template_name).exists():
            template_name = "page.html"

        template = env.get_template(template_name)

        # Recent posts for this page's language
        lang = page["language"]
        recent = posts_by_language.get(lang, [])[:config["recentPosts"]]

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
            languages=config["languages"],
            page=page,
            content=render_markdown(page["body"]),
            recent_posts=recent,
            posts=posts_by_language.get(lang, []),
            posts_by_language=posts_by_language,
            home=home_data,
            icons=icons,
            config=config,
        )

        html = _add_external_link_attrs(html, config["site"].get("url", ""))

        page["output_file"].parent.mkdir(parents=True, exist_ok=True)
        page["output_file"].write_text(html, encoding="utf-8")

    # ------------------------------------------------------------------
    # 5. Render post-list pages per language
    # ------------------------------------------------------------------
    all_langs = [config["languages"]["default"]] + config["languages"].get("additional", [])
    for lang in all_langs:
        posts = posts_by_language.get(lang, [])
        if not posts:
            continue

        if lang == config["languages"]["default"]:
            post_prefix = config.get("postPrefix", "")
            if post_prefix:
                list_url = f"/{post_prefix}/"
                list_output = DIST_DIR / post_prefix / "index.html"
            else:
                list_url = "/posts/"
                list_output = DIST_DIR / "posts" / "index.html"
        else:
            list_url = f"/{lang}/"
            list_output = DIST_DIR / lang / "index.html"

        template = env.get_template("post-list.html")
        html = template.render(
            site=config["site"],
            languages=config["languages"],
            page={"title": "Posts", "url": list_url, "language": lang},
            posts=posts,
            posts_by_language=posts_by_language,
            home=config.get("home", {}),
            icons=icons,
            config=config,
        )

        html = _add_external_link_attrs(html, config["site"].get("url", ""))

        list_output.parent.mkdir(parents=True, exist_ok=True)
        list_output.write_text(html, encoding="utf-8")

    # ------------------------------------------------------------------
    # 6. RSS feeds
    # ------------------------------------------------------------------
    if config["site"].get("url"):
        # Default language
        default_lang = config["languages"]["default"]
        default_posts = posts_by_language.get(default_lang, [])
        rss_path = DIST_DIR / config["rss"]["default"]
        build_rss(config, default_lang, default_posts, rss_path)

        # Additional languages
        for lang in config["languages"].get("additional", []):
            rss_path = DIST_DIR / config["rss"]["additional"].format(lang=lang)
            build_rss(config, lang, posts_by_language.get(lang, []), rss_path)

    # ------------------------------------------------------------------
    # 7. Copy CSS and static assets
    # ------------------------------------------------------------------
    # Copy package base CSS → dist/midas.css
    package_css = PACKAGE_STATIC_DIR / "style.css"
    if package_css.exists():
        shutil.copy2(package_css, DIST_DIR / "midas.css")

    # Copy project root style.css → dist/style.css (override)
    project_css = Path("style.css")
    if project_css.exists():
        shutil.copy2(project_css, DIST_DIR / "style.css")

    # Copy project static/ contents → dist/
    if STATIC_DIR.exists():
        for src in STATIC_DIR.rglob("*"):
            if src.is_file():
                dst = DIST_DIR / src.relative_to(STATIC_DIR)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

    # Copy content/img/ → dist/img/
    img_dir = CONTENT_DIR / "img"
    if img_dir.exists():
        dst_img = DIST_DIR / "img"
        if dst_img.exists():
            shutil.rmtree(dst_img)
        shutil.copytree(img_dir, dst_img)

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
