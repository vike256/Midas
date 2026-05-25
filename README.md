# Midas

A minimal static site generator. Put markdown in `site/`, run `midas serve`, get a website.

## Quick start

```bash
midas init my-blog
cd my-blog
midas serve
```

Or manually:

```
mkdir site
echo -e '---\ntitle: Hello\n---\n\nWelcome' > site/index.md
midas serve
```

Open `http://localhost:8000`.

## How it works

Your content lives in `site/`. Every `.md` file becomes a page. Everything else (images, CSS, fonts) is copied to `_dist/` as-is — the folder structure is your site structure.

```
site/
├── index.md       →  /
├── about.md       →  /about/
├── p/
│   └── post.md    →  /p/post/
├── style.css      →  /style.css
└── img/
    └── photo.jpg  →  /img/photo.jpg
```

### Blog posts

Files in `p/` (or your configured `postPrefix`) are treated as blog posts, sorted by date (set in frontmatter), and included in RSS feeds.

### Styles

Midas ships with a base stylesheet (`/midas.css`). Add overrides in `site/style.css` — it's loaded after the base.

## Commands

| Command | Description |
|---|---|
| `midas init [dir]` | Scaffold a project into an empty directory |
| `midas build` | Build the site to `_dist/` |
| `midas serve` | Build and start a dev server on `http://localhost:8000` |
| `midas clean` | Delete `_dist/` |

## Configuration

`midas.yaml` is optional. Without it, Midas uses sensible defaults. Set `site.url` for RSS feeds and `site.name` for the site header.

```yaml
site:
  url: "https://example.com"
  name: "My Site"

languages:
  default: en
  additional: [fi]
```

See the [configuration reference](/p/configuration/) for all available options.

## Deploying

Push to GitHub and connect to a static host:

- **GitHub Pages** — deploy via GitHub Actions
- **Cloudflare Pages** — set build command to `pip install midas-ssg && midas build`, output directory to `_dist`
