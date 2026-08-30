# Floor Plan Studio

Draw your flat to scale, arrange real furniture in it, and print a shopping list
with every size in centimetres. One self-contained HTML file — no build step, no
dependencies, no server, nothing uploaded.

**Live site:** https://tarekfouad97.github.io/Floor-Plan-Studio/

## Layout

| Path | What it is |
|---|---|
| `index.html` | Landing page — this is what GitHub Pages serves |
| `app.html` | The planner itself. The whole application, in one file |
| `privacy.html` | Privacy policy |
| `editor.html` | Working copy of the app, opened directly from disk (see below) |
| `planner.html` | The earlier "classic" planner, kept for saved plans that use it |
| `PLAN.md` | Design notes: why standalone HTML, why SVG, why cm-only |
| `trace/` | Python tooling used once to extract walls from the original sketch |
| `*.floorplan.json` | Saved plans |

## Keeping `editor.html` in sync

`editor.html` is a copy of `app.html` that differs by exactly one line: its
wordmark is a plain `<span>` rather than a link back to `index.html`, because the
working copy is opened on its own. After any change to `app.html`:

    cp app.html editor.html
    # then change the `<a class="home" href="index.html" …>` line back to
    # `<span class="home"><i>&#9636;</i>Floor Plan Studio</span>`

`diff app.html editor.html` should report that one line and nothing else.

## Cache-busting

Links to the app in `index.html` carry `?v=<build>`, matching the build string
shown in the app's status bar (`#stBuild`). Bump both together, or returning
visitors keep the old build from the GitHub Pages cache.

## Publishing

GitHub Pages serves **main / (root)** — the default, nothing to configure. Push to
`main` and the site updates.

To work on it locally with browser autosave enabled (a `file://` page cannot use
local storage):

    python3 -m http.server 8731
    # then open http://localhost:8731/app.html

## Before switching ads on

See `DEPLOYING.md` — cookie consent and content requirements if you add ads.
