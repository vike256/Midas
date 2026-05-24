---
title: "Configuration Reference"
description: "All midas.yaml options explained"
date: 2026-05-24
---

Everything in `midas.yaml` is optional — Midas works out of the box — but most sites will want at least `site.url` and some `home` settings.

## site

```yaml
site:
  url: "https://example.com"
  name: "My Site"
  description: "A personal website"
  copyright: "© 2025 Your Name"
  fediverse: "@user@example.com"
```

| Key | Description |
|---|---|
| `url` | Base URL. Enables RSS feeds and smart external-link handling. |
| `name` | Site name shown in the header and page titles. |
| `description` | Used in RSS feeds and the meta description tag. |
| `copyright` | Footer copyright text. Omit or leave empty to hide it. |
| `fediverse` | Fediverse handle. Adds a `<meta name="fediverse:creator">` tag for verification. |

## languages

```yaml
languages:
  default: en
  additional: [fi, sv]
```

Content for additional languages goes in subfolders: `content/fi/`, `content/sv/`. The `language` frontmatter field takes priority over folder inference.

## nav

```yaml
nav:
  - title: "Posts"
    url: "/p/"
  - title: "About"
    url: "/about/"
```

Controls the header. Three states:

- **Omitted** — no header at all (ideal for single-page Linktree-style sites)
- **`nav: []`** — header with just the site name as a home link
- **`nav: [{title, url}, ...]`** — header with site name + navigation links

## home

```yaml
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
```

| Key | Description |
|---|---|
| `name` | Displayed prominently on the homepage. |
| `bio` | Short text under the name. |
| `profilePic` | Path to a profile picture. If omitted, Midas auto-detects `content/img/profile.*` (png, jpg, jpeg, or webp). |
| `socials` | List of `{name, url}` links rendered as icons. Built-in icons match common names like `github`, `email`, etc. |
| `cards` | List of `{title, url}` link cards on the homepage. |

## postPrefix

```yaml
postPrefix: "p"
```

Sets the URL path for default-language posts. With `"p"`, posts live at `/p/my-post/` and the archive is `/p/`. Set to `""` to put posts at the root. Additional languages are unaffected — they use `/<lang>/`.

## recentPosts

```yaml
recentPosts: 3
```

Number of recent posts shown on the homepage per language.

## rss

```yaml
rss:
  default: "feed.xml"
  additional: "{lang}/feed.xml"
```

RSS feeds are only generated when `site.url` is set. The `{lang}` placeholder is replaced with each language code. Feed filenames determine the output path in `_dist/`.

## Custom 404 page

Create `content/404.md` to customize your error page:

```markdown
---
title: Page Not Found
---

The page you're looking for doesn't exist.

[Go back home](/)
```

It is rendered as `_dist/404.html`.