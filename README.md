# Floor Plan Studio

Draw your flat to scale, arrange real furniture in it, and print a shopping list
with every size in centimetres. No build step, no server, nothing uploaded.

**Live site:** https://tarekfouad97.github.io/Floor-Plan-Studio/

## Layout

| Path | What it is |
|---|---|
| `index.html` | Landing page — this is what GitHub Pages serves |
| `app.html` | The planner itself. The whole application, in one file |
| `guides.html` | Hub for the three reference pages |
| `furniture-sizes.html` | All 116 catalogue pieces, generated from `app.html` |
| `room-clearances.html` | Walkways and clearances |
| `measure-a-room.html` | How to measure a room |
| `about.html`, `terms.html`, `privacy.html` | About, terms, privacy policy |
| `site.css` | Shared shell for every page except `index.html` and the app |
| `ads.js` | Ad slots and the blocker note — one place for the publisher id |
| `editor.html` | Working copy of the app, opened directly from disk (see below) |
| `planner.html` | The earlier "classic" planner, kept for saved plans that use it |
| `vendor/three.module.min.js` | three.js r160, vendored (see below) |
| `robots.txt`, `sitemap.xml`, `ads.txt` | Search and ads plumbing |

`index.html` keeps its own inline CSS because the hero, the 3D stages and the
clearance widget are bespoke to it. Every other page uses `site.css`, so a change
to the header or footer there has to be made in two places, not eight.

`furniture-sizes.html` is generated from `app.html`'s `CATALOG`. If you add or
resize a piece in the planner, that page is out of date until it is regenerated —
the numbers are copied, not linked.
| `PLAN.md` | Design notes: why standalone HTML, why SVG, why cm-only |
| `trace/` | Python tooling used once to extract walls from the original sketch |
| `*.floorplan.json` | Saved plans |

## three.js

Both the landing page's models and the planner's 3D view use three.js. It is
**vendored into `vendor/`, never loaded from a CDN**, for two reasons: the site
claims in `privacy.html` to make no third-party requests, and that claim has to
survive inspection in a network tab.

The planner imports it *on demand* — the first time anyone opens the 3D view —
so the 2D planner still loads without it. That import is an ES module, which
means:

**The 3D view needs the page served over http, not opened from `file://`.**
It fails gracefully (a toast, and it drops back to the plan), but if you are
working locally, run the server below. You wanted it anyway: a `file://` page
cannot use local storage, so autosave is off without it.

To update three.js, replace the file and check the 3D view still draws. The
planner uses `WebGLRenderer`, `PerspectiveCamera`, `MeshStandardMaterial`,
`BufferGeometry`, `ShapeUtils.triangulateShape`, and the light classes.

## How the 3D view works

`buildScene()` produces the whole model as flat quads in world centimetres —
walls sectioned around their openings, furniture, the electrical layer. That
part is shared and unchanged. `build3()` turns those quads into one
`BufferGeometry` with vertex colours; three.js lights it. `shade()` steps aside
while this happens (the `RAW3` flag), because the quads must carry their true
colours rather than pre-baked shading.

The camera still lives in `V3` and is still driven by the same damped
navigation, so every control — the presets, orbit, pan, the cutaway, the sun by
time of day and north — works exactly as it did. `render3()` rebuilds geometry
and draws; `paint3()` only draws, and is what the drag path calls.

## Sharing a plan in a link

`File → Copy a link to this plan` encodes the whole document into the URL
fragment: deflate-raw, then base64url, behind a `#p1=` prefix (`#p0=` is the
uncompressed fallback for browsers without `CompressionStream`). Everything
after the `#` is never sent to a server, so this does not weaken anything
`privacy.html` claims.

The trace photograph is stripped — it is base64 raster and would dwarf the
plan. A furnished 8-room flat with 52 pieces and 40 fittings comes to about
5.6 KB of link; anything over 30,000 characters is refused with a nudge
towards `Save to file`.

Inbound links are handled on load **and** on `hashchange`, because pasting a
link into a tab that already has the planner open is a same-document
navigation — no reload, so a load-time handler alone would never fire.

## Exporting part of a plan

`File → Export plan data…` asks what to include. Walls, doors, windows and
rooms always go; furniture, the electrical layer and the trace image are each
optional. Dropping the electrical layer also drops moods and circuits, which
are keyed to fitting ids and mean nothing without them. The filename says what
happened — `-no-furniture`, `-no-electrical`, `-shell`. The copy on screen is
never modified.

## Keeping `editor.html` in sync

`editor.html` is a copy of `app.html` that differs in exactly two places:

1. its wordmark is a plain `<span>` rather than a link back to `index.html`,
   because the working copy is opened on its own;
2. it carries `<meta name="robots" content="noindex,nofollow">` instead of
   `app.html`'s canonical link, so the working copy stays out of search.

After any change to `app.html`:

    cp app.html editor.html
    # then put those two differences back

`diff app.html editor.html` should report those two hunks and nothing else.

## Cache-busting

Links to the app in `index.html` and `privacy.html` carry `?v=<build>`,
matching the build string shown in the app's status bar (`#stBuild`). Bump both
together, or returning visitors keep the old build from the GitHub Pages cache.

## Publishing

GitHub Pages serves **main / (root)** — the default, nothing to configure. Push
to `main` and the site updates.

To work on it locally:

    python3 -m http.server 8731
    # then open http://localhost:8731/app.html

## Ads

Slots are in place on the landing page and switched off. See `DEPLOYING.md`.
