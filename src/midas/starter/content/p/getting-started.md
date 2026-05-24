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

Or scaffold into a new folder:

```bash
midas init my-blog
cd my-blog
```

## Project layout

After `midas init`, your project looks like this:

```
my-blog/
├── midas.yaml          # Site configuration
├── style.css           # Optional CSS overrides (empty by default)
├── content/            # Your markdown content
│   ├── index.md        # Homepage
│   ├── p/              # Blog posts (matches postPrefix)
│   └── img/            # Images (copied as-is to dist/)
└── static/             # Other static assets (favicons, fonts, etc.)
```

The built site is written to `dist/`.

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

### Homepage

`content/index.md` with `type: home` becomes the homepage.

## Building for production

When you are ready to publish, run:

```bash
midas build
```

This generates the static site in `dist/`.

## Deploying

Upload the contents of `dist/` to a static host:

- **GitHub Pages** — deploy via GitHub Actions
- **Cloudflare Pages** — connect your repo and set the build command to `midas build`

## Customizing your site

### CSS overrides

Edit `style.css` at your project root. It is loaded after the built-in `midas.css`, so any rule you write overrides the base. For example, to switch to dark mode:

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

Then edit `templates/home.html`. When you run `midas build`, you will see a warning that the template is overridden and will no longer receive automatic updates.

### Configuration

Edit `midas.yaml` to set your site name, URL, social links, and more:

```yaml
site:
  url: "https://example.com"
  name: "My Site"
  description: "A personal website"

home:
  name: "Your Name"
  bio: "A short description about you."
  profilePic: "/img/profile.webp"
  socials:
    - name: github
      url: "https://github.com/yourusername"
```

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
| `midas clean` | Delete the `dist/` folder |

That is everything you need to get started. Now go build something.
