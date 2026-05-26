---
title: "Start using Midas"
description: "How to install, set up, and start building your site"
date: 2026-05-23
type: post
---

This guide walks you through installing Midas and creating your first site.

## Installation

Midas requires Python 3.9 or newer.

```bash
pip install midas-ssg
```

This installs the `midas` command-line tool.

## Create a new site

Run `midas init` to scaffold a project into the current directory. The directory must be empty:

```bash
midas init
```

## Project layout

After `midas init`, your project looks like this:

```
my-blog/
├── .gitignore          # Ignores _dist/, virtual environments, etc.
├── midas.yaml          # Site configuration
└── site/               # Your site content
    ├── index.md        # Homepage
    ├── 404.md          # Not-found page
    ├── favicon.svg     # Site icon
    ├── style.css       # Your CSS overrides
    ├── p/              # The "p" collection (posts)
    └── img/            # Images
```

The built site is written to `_dist/`.

## Preview your site

Start the built-in development server:

```bash
midas serve
```

Open `http://localhost:8000` to see your site. The server automatically picks the next available port if 8000 is in use.

## Writing content

### Posts

Configure your collections in `midas.yaml`, then create content under matching directories in `site/`:

```yaml
# midas.yaml
collections:
  p:
    title: "Posts"
    language: en
    feed: "/feed.xml"
  notes:
    title: "Notes"
    language: en
    feed: "/feed.xml"     # merged into the same feed as Posts
```

```
# Directory structure
site/
├── p/hello-world.md       # → belongs to "p" collection
├── notes/my-thoughts.md   # → belongs to "notes" collection
└── about.md               # → standalone page (no type: post)
```

Each collection directory maps to a name in `midas.yaml`. Markdown files under it with `type: post` in frontmatter belong to that collection:

```markdown
---
title: "Hello World"
description: "My first post"
date: 2026-05-23
type: post
---
```

A post at `site/p/hello-world.md` appears at `/p/hello-world/`, is listed on the collection archive page, and is included in the RSS feed. Since both `p` and `notes` set `feed: "/feed.xml"`, posts from both collections are merged into a single feed sorted by date.

### Pages

A markdown file without `type: post` becomes a standalone page. For example, `site/about.md` renders at `/about/`. Pages are not part of any collection and do not appear in RSS feeds.

Add pages to `midas.yaml` under `nav:` if you want them in the top navigation:

```yaml
nav:
  - title: "About"
    url: "/about/"
```

### Homepage

`site/index.md` is your homepage. Most of the content is configured in `midas.yaml` under `home:`.

## Building and deploying

When you are ready to publish, run:

```bash
midas build
```

This generates the static site in `_dist/`.

Push your project to GitHub and connect it to a static host:

- **GitHub Pages** — deploy via GitHub Actions
- **Cloudflare Pages** — connect your repo and use the following settings:
  - Build command: `pip install midas-ssg && midas build`
  - Build output: `_dist`
  - Make it automatic with [Deploy Hooks](https://developers.cloudflare.com/pages/configuration/deploy-hooks/)

## Customizing your site

### CSS overrides

Edit `site/style.css`. It is loaded after the built-in `midas.css`, so any rule you write overrides the base. For example, to switch to dark mode:

```css
body {
  background: #1a1a1a;
  color: #fafafa;
}
```

### Configuration

Edit `midas.yaml` to set your site name, URL, social links, and more. See the [configuration reference](/p/configuration/) for every available option.

### Multilingual sites

Create one collection per language:

```yaml
collections:
  en:
    title: "Posts"
    language: en
    feed: "/feed.xml"
  fi:
    title: "Suomi"
    language: fi
    feed: "/fi/feed.xml"
```

Finnish posts go in `site/fi/` with `type: post`. Each collection gets its own listing page, RSS feed, and the `<language>` tag in RSS comes from the collection config.

## Markdown features

Midas supports standard Markdown plus these built-in extensions:

**Fenced code blocks**

````markdown
```python
def hello():
    print("Hello, world!")
```
````

**Tables**

```markdown
| Name  | Role   |
|-------|--------|
| Alice | Admin  |
| Bob   | User   |
```

**Table of contents**

Place `[TOC]` in your markdown where you want the table of contents to appear.

**Syntax highlighting**

Use fenced code blocks with a language tag. Requires Pygments.

**Strikethrough**

```markdown
~~This text is struck through.~~
```

**Attribute lists**

Attach HTML attributes (`id`, `class`, etc.) to block and inline elements:

```markdown
This paragraph is special.
{: .lead }

[Read more](about.html){: class="button" }
```

## Other commands

| Command | Description |
|---|---|
| `midas clean` | Delete the `_dist/` folder |

That is everything you need to get started. Now go build something.
