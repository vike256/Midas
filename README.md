# Midas

A minimal, opinionated static site generator. Drop markdown files into a folder, run one command, and get a clean, fast, multilingual website.

## Features

- **Zero config** for single-language sites
- **Markdown** with syntax highlighting, tables, and strikethrough
- **Multilingual** support as a first-class feature
- **RSS feeds** per language
- **Built-in templates and CSS** that update with the package
- **Jinja2 templates** — optional override for power users
- **Built-in dev server** — no extra tools needed

## Installation

Requires Python 3.9 or newer.

```bash
pip install midas-ssg
```

Or install from source in editable mode for development:

```bash
pip install -e .
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
| `midas build` | Build the site to `dist/`. |
| `midas serve` | Build and start a local development server on `http://localhost:8000`. |
| `midas clean` | Delete the `dist/` folder. |

## Directory structure

After `midas init`, your project looks like this:

```
my-blog/
├── midas.yaml          # Site configuration
├── style.css           # Optional CSS overrides (empty by default)
├── content/            # Your markdown content
│   ├── index.md        # Homepage
│   ├── posts/          # Blog posts
│   └── img/            # Images (copied as-is)
└── static/             # Other static assets (favicons, fonts, etc.)
```

The built site is written to `dist/`.

## How it works

### Templates

Midas ships with built-in Jinja2 templates (`base.html`, `home.html`, `post.html`, etc.) that live inside the installed package. When you update Midas (`pip install -U midas`), your site's HTML updates automatically.

You never have to touch HTML. If you want to customize a template, create a `templates/` folder in your project and copy only the files you want to override. Midas will use your version instead of the built-in one, but you'll stop receiving updates for those specific templates.

### Styles

Midas provides a built-in light minimalist stylesheet. It is copied to `dist/midas.css` on every build.

To customize styles, edit the `style.css` file at your project root. It is copied to `dist/style.css` and loaded **after** `midas.css`, so any rule you write overrides the base. Keep your overrides minimal — only change what you need.

For other assets (favicons, fonts, PDFs), drop them into `static/` and they are copied to `dist/`.

## Writing content

### Blog posts

Create a markdown file in `content/posts/`:

```markdown
---
title: "Hello World"
description: "My first post"
date: 2025-01-01
---

Your post content here.
```

Posts are sorted by date. The filename can also include a date prefix: `2025-01-01-hello-world.md`.

### Standalone pages

Any `.md` file outside `posts/` becomes a page:

```markdown
---
title: "About"
---

This is the about page.
```

### Homepage

`content/index.md` with `type: home` becomes the homepage. You can put metadata in its frontmatter or in `midas.yaml` under `home:`.

### Multilingual content

Add languages in `midas.yaml`:

```yaml
languages:
  default: en
  additional: [fi]
```

Then create content in `content/fi/posts/` for Finnish posts. Frontmatter `language` takes priority over folder inference.

## Configuration

`midas.yaml` is optional but recommended:

```yaml
site:
  url: "https://example.com"
  name: "My Site"
  description: "A personal website"
  copyright: "© 2024 Your Name"

languages:
  default: en
  additional: [fi]

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

recentPosts: 3
```

## Customization

### CSS overrides

Edit `style.css` at your project root. For example, to switch to a dark background:

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

## Dependencies

- [markdown](https://pypi.org/project/Markdown/) — Markdown parsing
- [Pygments](https://pygments.org/) — Syntax highlighting
- [Jinja2](https://jinja.palletsprojects.com/) — Templating
- [PyYAML](https://pyyaml.org/) — YAML parsing

## License

MIT
