# Midas

A minimal, opinionated static site generator. Drop markdown files into a folder, run one command, and get a clean, fast, multilingual website.

## Features

- **Zero config** for single-language sites
- **Markdown** with syntax highlighting, tables, strikethrough, inline HTML, and table of contents
- **Multilingual** support as a first-class feature
- **RSS feeds** per language
- **Built-in templates and CSS** that update with the package
- **Jinja2 templates** — optional override for power users
- **Built-in dev server** — no extra tools needed
- **Custom 404 page** — just add `content/404.md`
- **Smart external links** — automatically adds `target="_blank"` and `rel="noopener noreferrer"` to links outside your site

## Installation

Requires Python 3.9 or newer.

```bash
pip install midas-ssg
```

This installs the `midas` command-line tool.

## Quick start

```bash
midas init my-blog
cd my-blog
midas serve
```

Open `http://localhost:8000` to see your site.

## Commands

| Command | Description |
|---|---|
| `midas init <folder>` | Scaffold a new Midas project into `<folder>`. Requires an empty directory. |
| `midas init` | Scaffold a new Midas project into the current directory. Also requires an empty directory. |
| `midas build` | Build the site to `_dist/`. |
| `midas serve` | Build and start a local dev server. Defaults to `http://localhost:8000`; picks the next available port if busy. |
| `midas clean` | Delete the `_dist/` folder. |

## Deploying

Upload the contents of `_dist/` to a static host:

- **GitHub Pages** — deploy via GitHub Actions
- **Cloudflare Pages** — connect your repo and set the build command to `midas build`

## Directory structure

After `midas init`, your project looks like this:

```
my-blog/
├── .gitignore          # Ignores _dist/, virtual environments, etc.
├── midas.yaml          # Site configuration
├── content/            # Your markdown content
│   ├── index.md        # Homepage
│   ├── p/              # Blog posts (matches postPrefix)
│   └── img/            # Images (copied as-is)
└── static/             # Other static assets (favicons, fonts, etc.)
```

The built site is written to `_dist/`.

## How it works

### Templates

Midas ships with built-in Jinja2 templates (`base.html`, `home.html`, `post.html`, etc.) that live inside the installed package. When you update Midas (`pip install -U midas-ssg`), your site's HTML updates automatically.

You never have to touch HTML. If you want to customize a template, create a `templates/` folder in your project and copy only the files you want to override. Midas will use your version instead of the built-in one, but you'll stop receiving updates for those specific templates.

### Styles

Midas provides a built-in light minimalist stylesheet. It is copied to `_dist/midas.css` on every build.

To customize styles, edit `static/style.css`. It is copied to `_dist/style.css` and loaded **after** `midas.css`, so any rule you write overrides the base. Keep your overrides minimal — only change what you need.

For other assets (favicons, fonts, PDFs), drop them into `static/` and they are copied to `_dist/`.

## Writing content

### Blog posts

Create a markdown file in `content/p/`:

```markdown
---
title: "Hello World"
description: "My first post"
date: 2025-01-01
---

Your post content here.
```

Posts are sorted by date. The date must be set in frontmatter — it is not inferred from the filename.

### Standalone pages

Any `.md` file outside `p/` becomes a page:

```markdown
---
title: "About"
---

This is the about page.
```

### Homepage

`content/index.md` automatically becomes the homepage (the `type: home` frontmatter is inferred for `index.md`). You can put metadata in its frontmatter or in `midas.yaml` under `home:`.

### Multilingual content

Add languages in `midas.yaml`:

```yaml
languages:
  default: en
  additional: [fi]
```

Then create content in `content/fi/` for Finnish posts. Frontmatter `language` takes priority over folder inference.

## Configuration

`midas.yaml` is optional but recommended:

```yaml
site:
  url: "https://example.com"
  name: "My Site"
  description: "A personal website"
  copyright: "© 2025 Your Name"
  fediverse: "@user@example.com"

languages:
  default: en
  additional: [fi]

nav:
  - title: "Posts"
    url: "/p/"
  - title: "About"
    url: "/about/"

home:
  name: "Your Name"
  bio: "A short description about you."
  profilePic: "/img/profile.webp"
  socials:
    - name: github
      url: "https://github.com/yourusername"
    - name: email
      url: "mailto:hello@example.com"
  cards:
    - title: "My Project"
      url: "https://example.com/project"

postPrefix: "p"
recentPosts: 3
rss:
  default: "feed.xml"
  additional: "{lang}/feed.xml"
```

`postPrefix` sets the URL path for default-language posts and their archive page. With the default `"p"`, posts live at `/p/my-post/` and the archive is `/p/`. Additional languages are unaffected — they use `/<lang>/my-post/` and `/<lang>/`.

### Config keys

| Key | Description |
|---|---|
| `site.url` | Your site's base URL. Enables RSS feeds and smart external-link handling. |
| `site.name` | Site name shown in the header and page titles. |
| `site.description` | Site description used in RSS feeds. |
| `site.copyright` | Footer copyright text. Hide it by leaving empty. |
| `site.fediverse` | Fediverse handle (e.g. `@user@example.com`). Adds a `<meta name="fediverse:creator">` tag. |
| `languages.default` | Default language code (e.g. `en`). |
| `languages.additional` | List of additional language codes (e.g. `[fi, sv]`). |
| `nav` | Controls the header. Omitted = no header at all. `nav: []` = header with just the site name. `nav: [...]` = header with site name + navigation links. |
| `home.name` | Name displayed on the homepage. |
| `home.bio` | Short bio on the homepage. |
| `home.profilePic` | Path to a profile picture. Auto-detected from `content/img/profile.*` if not set. |
| `home.socials` | List of `{name, url}` social links. Rendered as icons. |
| `home.cards` | List of `{title, url}` link cards on the homepage. |
| `postPrefix` | URL prefix for default-language posts (default `"p"`). |
| `recentPosts` | Number of recent posts shown on the homepage (default `3`). |
| `rss.default` | Filename for the default-language RSS feed (default `feed.xml`). |
| `rss.additional` | Filename pattern for additional-language feeds. Use `{lang}` as a placeholder (default `{lang}/feed.xml`). |

## Customization

### CSS overrides

Edit `static/style.css`. For example, to switch to a dark background:

```css
body {
  background: #1a1a1a;
  color: #fafafa;
}
```

### Template overrides

Create a `templates/` folder and drop in only the files you want to override. For example, to customize the homepage:

```bash
mkdir templates
cp $(python -c "import midas; print(midas.__file__)")/../templates/home.html templates/
```

Then edit `templates/home.html`. When you run `midas build`, you'll see a warning:

```
Templates overridden: home.html
These will not receive updates from Midas automatically.
```

### Icons

The built-in `home.html` template renders social icons by looking up SVG files in `templates/icons/` by name. If you create a `templates/icons/` folder in your project, you can add or replace icons there.

### 404 page

Create `content/404.md` to customize your 404 page. It is rendered as `_dist/404.html`.

### Footer credit

The built-in `base.html` template includes a "Created with Midas" link in the footer. Override the template if you'd like to remove or change it.

## Dependencies

- [markdown](https://pypi.org/project/Markdown/) — Markdown parsing
- [Pygments](https://pygments.org/) — Syntax highlighting
- [Jinja2](https://jinja.palletsprojects.com/) — Templating
- [PyYAML](https://pyyaml.org/) — YAML parsing

## License

MIT
