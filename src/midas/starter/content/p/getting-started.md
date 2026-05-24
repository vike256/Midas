---
title: "Getting Started with Midas"
description: "How to install, set up, and start building your site"
date: 2026-05-23
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
├── content/            # Your markdown content
│   ├── index.md        # Homepage
│   ├── 404.md          # Not-found page
│   ├── p/              # Blog posts (matches postPrefix)
│   └── img/            # Images (copied as-is to _dist/)
└── static/             # Other static assets
    ├── style.css       # Your CSS overrides
    └── favicon.svg     # Site icon
```

The built site is written to `_dist/`.

## Preview your site

Start the built-in development server:

```bash
midas serve
```

Open `http://localhost:8000` to see your site. The server automatically picks the next available port if 8000 is in use.

## Writing content

### Blog posts

Create a markdown file in `content/p/`:

```markdown
---
title: "Hello World"
description: "My first post"
date: 2026-05-23
---

Your post content here.
```

### Standalone pages

Any `.md` file outside `p/` becomes a page. For example, `content/about.md` becomes `/about/`.

Add standalone pages to `midas.yaml` under `nav:` if you want them in the top navigation:

```yaml
nav:
  - title: "About"
    url: "/about/"
```

### Homepage

`content/index.md` is your homepage. Most of the content is configured in `midas.yaml` under `home:`.

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

Edit `static/style.css`. It is loaded after the built-in `midas.css`, so any rule you write overrides the base. For example, to switch to dark mode:

```css
body {
  background: #1a1a1a;
  color: #fafafa;
}
```

### Configuration

Edit `midas.yaml` to set your site name, URL, social links, and more. See the [configuration reference](/p/configuration/) for every available option.

### Multilingual sites

Add languages in `midas.yaml`:

```yaml
languages:
  default: en
  additional: [fi]
```

Then create content in `content/fi/` for Finnish posts. Frontmatter `language` takes priority over folder inference.

## Other commands

| Command | Description |
|---|---|
| `midas clean` | Delete the `_dist/` folder |

That is everything you need to get started. Now go build something.
