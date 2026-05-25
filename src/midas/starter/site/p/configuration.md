---
title: "Configuration Reference"
description: "All midas.yaml options explained"
date: 2026-05-24
type: post
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
|---|---|---|
| `url` | Base URL. Enables RSS feeds and smart external-link handling. |
| `name` | Site name shown in the header and page titles. |
| `description` | Used in RSS feeds and the meta description tag. |
| `default_language` | Fallback language for pages and RSS when nothing else is specified. |
| `copyright` | Footer copyright text. Omit or leave empty to hide it. |
| `fediverse` | Fediverse handle. Adds a `<meta name="fediverse:creator">` tag for verification. |

## collections

```yaml
collections:
  p:
    title: "Posts"
    language: en
    feed: "/feed.xml"
  notes:
    title: "Notes"
    language: en
    feed: "/feed.xml"     # merges into /feed.xml alongside posts
  shorts:
    title: "Short Thoughts"
    language: en
    # no feed → no RSS
```

Define content groups. Each collection:
- Maps to a directory under `site/` (e.g., `site/p/` for collection `p`)
- Includes markdown files with `type: post` in that directory
- Gets an auto-generated listing page at `/{name}/`
- Optionally generates an RSS feed at the path set by `feed`
  - **Multiple collections can push to the same feed path** — posts are merged and sorted by date.
  - Omit `feed` entirely to exclude a collection from RSS.

| Key | Description |
|---|---|
| `title` | Display name for listing pages and RSS feed |
| `language` | Language code for RSS `<language>` tag. Omit to leave it out of the feed. |
| `feed` | RSS output path like `"/feed.xml"` or `"/notes/feed.xml"` |

For multilingual sites, create one collection per language. A `fi` collection maps to `site/fi/` — Finnish posts live there and get their own RSS feed.

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
| `profilePic` | Path to a profile picture. If omitted, Midas auto-detects `site/img/profile.*` (png, jpg, jpeg, or webp). |
| `socials` | List of `{name, url}` links rendered as icons. Built-in icons match common names like `github`, `email`, etc. |
| `cards` | List of `{title, url}` link cards on the homepage. |

## recentPosts

```yaml
recentPosts: 3
```

Number of recent posts shown on the homepage per collection.

## Custom 404 page

Create `site/404.md` to customize your error page:

```markdown
---
title: Page Not Found
---

The page you're looking for doesn't exist.

[Go back home](/)
```

It is rendered as `_dist/404.html`.