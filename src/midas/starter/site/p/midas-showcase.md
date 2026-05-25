---
title: "Midas Markdown Showcase"
description: "A tour of the markdown features available out of the box"
date: 2026-05-24
type: post
---

Welcome to your new Midas site. This post is a quick tour of the markdown features you can use right out of the box.

## Text formatting

You can write **bold text**, *italic text*, or ~~strikethrough~~. You can also combine them: ***bold and italic***.

## Links and images

Here is a [link to example.com](https://example.com).

Images use standard markdown syntax:

![A watch](/img/watch.webp)

## Lists

Unordered list:

- First item
- Second item
  - Nested item
  - Another nested item
- Third item

Ordered list:

1. Step one
2. Step two
3. Step three

## Blockquotes

> "The best time to plant a tree was twenty years ago. The second best time is now."
>
> — Chinese proverb

## Code

Inline code looks like `print("hello")`.

Fenced code blocks get syntax highlighting:

```python
def greet(name):
    """Say hello to someone."""
    message = f"Hello, {name}!"
    print(message)
    return message

greet("World")
```

```javascript
function greet(name) {
  const message = `Hello, ${name}!`;
  console.log(message);
  return message;
}

greet("World");
```

## Tables

| Feature     | Supported |
|-------------|-----------|
| Markdown    | Yes       |
| Frontmatter | Yes       |
| RSS feeds   | Yes       |
| Multilingual| Yes       |

## Horizontal rule

---

## Inline HTML

Because `md_in_html` is enabled, you can drop in raw HTML when you need it:

<div style="padding: 1rem; background: #f0f0f0; border-radius: 8px;">
  <p>This is a custom HTML block inside markdown.</p>
</div>

## Table of Contents

The `toc` extension is enabled, but Midas does not auto-insert a TOC. If your template supports it, you can generate one with the `toc` markdown extension.

---

That covers the basics. Now go write something real.
