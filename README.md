# Floor Plan Studio

Draw your flat to scale, arrange real furniture in it, and print a shopping list
with every size in centimetres. One self-contained HTML file — no build step, no
dependencies, no server, nothing uploaded.

**Live site:** https://tarekfouad97.github.io/Floor-Plan-Studio/

## Layout

| Path | What it is |
|---|---|
| `docs/index.html` | Landing page — this is what GitHub Pages serves |
| `docs/app.html` | The planner itself. The whole application, in one file |
| `docs/privacy.html` | Privacy policy (still a draft — fill in the bracketed parts) |
| `editor.html` | Working copy of the app, opened directly from disk |
| `PLAN.md` | Design notes: why standalone HTML, why SVG, why cm-only |
| `trace/` | Python tooling used once to extract walls from the original sketch |
| `*.floorplan.json` | Saved plans |

## Publishing

GitHub Pages is set to serve **main / docs**. Push to `main` and the site updates.

To work on it locally with browser autosave enabled (a `file://` page cannot use
local storage):

    python3 -m http.server 8731 --directory docs
    # then open http://localhost:8731/app.html

## Before switching ads on

See `docs/README.md` — privacy policy, cookie consent and content requirements.
