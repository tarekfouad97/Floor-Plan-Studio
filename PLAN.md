# Apartment Furniture Planner — Project Plan

A 2D drag-and-drop furniture planner for the apartment in `IMG_1933.jpeg`.
Purpose: lay out furniture, read every size in **centimetres**, and print the
plan plus a shopping list to take to the furniture shop.

---

## 1. Goal

- Drag furniture from a catalogue list onto a scaled floor plan.
- Every placed item shows its real size in cm (W × D).
- Print or export the finished design as a picture, plus a shopping list
  with measurements, so furniture can be bought against real numbers.
- **2D only.** No 3D, no rendering, no visualisation beyond the plan view.

---

## 2. Source drawing

Original sketch is at scale 1:60, dimensioned in metres.

| Space | Size (m) | Area | Notes |
|---|---|---|---|
| Large room, top-left | 3.60 × 3.73 | ~13.4 m² | Also carries a 4.60 depth dim — see open questions |
| Room 2 | 3.60 × 3.48 | 12.5 m² | |
| Room 3 | 3.50 × 3.48 | 12.2 m² | |
| Room 4, top-right | 3.60 × 5.10 | 18.4 m² | Largest room |
| Balcony, top-right | 1.10 × 2.00 | 2.2 m² | |
| Terrace / L-strip, right | 5.81 × 3.10 | ~18 m² | |
| Bathroom | 1.42 × 2.20 | 3.1 m² | |
| Small room | 2.06 × 1.32 | 2.7 m² | |
| Toilet / utility | 1.60 × 2.32 | 3.7 m² | |
| Kitchen | 3.35 × 2.32 | 7.8 m² | |
| Corridor | 1.00 wide | — | |

Overall envelope ≈ **15.40 m × 11 m**.
Top row widths: 3.60 + 3.60 + 3.50 + 3.60 + 1.10 = 15.40 m.

Doors and their swing arcs are marked on the drawing and will be traced too —
they matter for clearance checking.

---

## 3. Stack decisions

### Standalone HTML file — no Google Apps Script

Originally scoped as an Apps Script web app. Dropped, because the whole
application is a single self-contained HTML file and Apps Script only wraps
and serves that file.

| | Standalone HTML | Apps Script |
|---|---|---|
| Deploy | none — double-click to open | publish + redeploy each change |
| Offline | yes | no |
| Printing | native, works | runs in a sandboxed iframe; `window.print()` unreliable |
| Shareable URL | no | yes |
| Cloud saves | no (localStorage / file export) | yes, via Drive |

Standalone wins on the thing that matters most here: **printing works with no
workaround.** If a shareable link and Drive saves are wanted later, wrapping
the same file in Apps Script is ~20 lines of `Code.gs`. Nothing is wasted.

### Not Python

The interactive layer — drag, live size readout, click-to-select — has to run
in the browser, in JavaScript. A Python web backend (Flask/FastAPI) would
require writing that same JS frontend *plus* running a server: more parts,
no gain. Streamlit and Gradio are built for forms and dashboards, not for
manipulating objects on a canvas.

The one genuine Python alternative is a **PyQt desktop app** (`QGraphicsView`
is excellent for this, and `QPrinter` handles printing well), but it only runs
where Python and Qt are installed — not on a phone in the shop, and sharing it
means packaging an installer. Rejected on distribution grounds.

Python may still be used as **build-time tooling** (generating catalogue JSON,
validating traced geometry). Not as the app.

### SVG, not Canvas

Every furniture item becomes a real DOM element, so hit-testing, selection and
hover labels come free, and output prints vector-sharp at any size. Canvas
would mean hand-writing hit-testing for no benefit.

### Pointer Events, not HTML5 drag-and-drop

Native `dragstart`/`drop` is fine for pulling an item *from* the catalogue
list. It is clumsy for moving items already on the plan — no live position
feedback, awkward on touch. On-canvas manipulation uses
`pointerdown` / `pointermove` / `pointerup` so size and position update live
while dragging.

---

## 4. The core rule

> **Everything is stored in centimetres. Pixels exist only at render time.**

A single `pxPerCm` factor converts between them. Every item stores
`{x, y, w, d, rot}` in cm. Zoom changes `pxPerCm` and nothing else.

This is what makes the measurements trustworthy. If pixel positions are ever
stored, the numbers drift and the tool loses its entire purpose.

---

## 5. Walls as data, not a background image

The shortcut would be to drop the JPEG in as a background and draw on top.
Rejected:

- The image is covered in dimension arrows, text and grid lines — visual noise
  to drag furniture through, and it prints badly.
- A photo cannot tell the app where a wall is: no wall-snapping, no
  "which room is this sofa in" logic.
- It is a photo of a drawing — there is perspective skew, and the scale is
  approximate.

Instead the plan is traced once into a JSON model, in cm, taken from the
**printed dimension labels** rather than measured off pixels. Those numbers are
exact. Result: furniture snaps to walls, the app knows which room each item
occupies, and printed output is clean line art.

### Data model

```js
const PLAN = {
  units: "cm",
  walls: [ { x1, y1, x2, y2, thickness } ],
  doors: [ { x, y, width, wall, swing: "in-left" | "in-right" | ..., } ],
  windows: [ { x, y, width, wall } ],
  rooms: [ { id, name, polygon: [[x,y], ...] } ]
};

const items = [
  { id, catalogId, name, x, y, w, d, rot, roomId, color, shape }
];
```

---

## 6. Features

Ranked by how directly they serve the goal of buying furniture.

1. **Live size badge** — while dragging, a label pinned to the item reads
   `200 × 90 cm`. Selected items keep the label permanently.
2. **Editable dimensions** — select an item, type a real number over the
   default. Actual furniture is never exactly the catalogue size, so the tool
   must bend to whatever is found in the shop.
3. **Shopping list panel** — auto-built table: item, room, W × D in cm,
   quantity, notes, price. Prints as page 2. This is the sheet carried to
   the store.
4. **Clearance warnings** — flag walkways under 75 cm, furniture fouling a
   door swing, under 60 cm in front of a wardrobe. Cheap to build, catches
   expensive mistakes.
5. **Wall snapping + rotation** — furniture sits against a wall most of the
   time. Snap within 10 cm; `R` rotates 90°, Shift-drag rotates freely.
6. **Tape-measure tool** — click two points, read the distance in cm. Used
   constantly to answer "will it fit through the door".
7. **Save / load** — layouts to `localStorage`, plus export/import as a JSON
   file so designs survive and can be compared.

---

## 7. Catalogue

~90–100 items, each with realistic standard dimensions in cm, a category
colour, and a shape type (`rect`, `circle`, `L`).

**Living** — 3-seat sofa 200×90, 2-seat 150×90, armchair 90×85, L-sofa
260×180, coffee table 110×60, round coffee 90⌀, TV unit 180×45, side table
50×50, console 120×40, bookshelf 80×35, rug 200×300, pouf 45⌀

**Dining** — table 4-seat 120×80, 6-seat 160×90, 8-seat 200×100, round 120⌀,
chair 45×45, sideboard 160×45, china cabinet 120×45

**Bedroom** — king bed 180×200, queen 160×200, double 140×200, single 90×200,
kids 120×200, crib 120×60, nightstand 45×40, wardrobe 2-door 100×60,
3-door 150×60, 4-door 200×60, corner wardrobe 100×100, dresser 120×50,
dressing table 100×45, chest of drawers 80×45, bench 100×40

**Office** — desk 120×60, large desk 140×70, office chair 60×60,
filing cabinet 40×50

**Kitchen** — base cabinet 60×60 / 80×60 / 100×60, corner base 90×90,
sink unit 80×60, cooker 60×60 / 90×60, fridge 60×65, side-by-side fridge
90×70, dishwasher 60×60, washing machine 60×60, tall pantry 60×60,
island 180×90, breakfast bar 120×60, microwave 50×40

**Bathroom** — toilet 40×70, bidet 40×60, vanity 60×50 / 80×50 / 100×50,
bathtub 170×75 / 150×70, shower tray 90×90 / 80×80 / 120×80,
towel cabinet 40×35, water heater 45×45

**Hall & misc** — shoe cabinet 90×35, coat rack 50×35, mirror 60×10,
AC split unit 90×25, plant 40⌀

Defined as one JSON array so adding items later is a one-line edit.

---

## 8. Build phases

| Phase | Deliverable | Done when |
|---|---|---|
| **1. Wall model** | Trace plan into JSON; render shell in SVG with room labels | On-screen dimensions match the drawing |
| **2. Catalogue + drag-drop** | Sidebar list, drag onto plan, move, rotate, delete, undo | Furniture can be placed and rearranged |
| **3. Measurement layer** | Size badges, editable dims, tape measure, clearance checks | Every item reads its size in cm |
| **4. Print & export** | A4 landscape print view, shopping list table, PNG download | A usable sheet comes out of the printer |
| **5. Save / load** | localStorage + JSON export, multiple named layouts | Designs survive a browser restart |

Phases 1–2 produce something genuinely usable. Phases 3–5 are what make it
worth printing.

---

## 9. Open questions

- **Left room geometry.** The top-left area carries both a 3.73 and a 4.60
  vertical dimension. Current reading: an L-shaped open area rather than a
  simple rectangle. To be confirmed against the traced output in phase 1,
  where corrections are cheap.
- **Room names.** The drawing does not say which room is the master bedroom,
  which is a child's room, or which is the reception. Rooms ship numbered and
  are renamed inside the app — better than guessing.
- **Pillow not installed.** Programmatic pixel analysis of the JPEG would need
  `pip install Pillow`. Likely unnecessary: the drawing is fully dimensioned,
  so geometry comes from the printed labels, not from measuring pixels. Only
  worth installing if an ambiguity cannot be resolved by hand.

---

## 10. IMPORTANT — the sketch is not drawn to scale

Measured from the image during phase 1. Calibration is solid: the footer's
0.5 m grid measures exactly **35 px in both axes** (0.70 px/cm), confirmed
independently in x and y, so the image itself is not stretched.

Against that scale, the drawn geometry and the written labels disagree:

| Dimension | Label | Drawn | Error |
|---|---|---|---|
| Reception width | 3.60 m | ~3.71 m | +3% |
| Bedroom 1 width | 3.60 m | ~3.69 m | +2% |
| Reception height | 3.73 m | ~4.26 m | **+14%** |
| Bedroom 1 depth | 3.48 m | ~4.07 m | **+17%** |
| Bathroom depth | 2.20 m | ~2.67 m | **+21%** |

Horizontal dimensions are close (2–3%); vertical ones are out by 14–21%.
There is also an internal contradiction: the 3.48 m dimension is drawn
**longer** on paper than the 3.73 m one. No single scale can produce that,
so the sketch's proportions are approximate and the **labels are the real
measurements**.

### What was done about it

The app is built from the **labelled dimensions**, not from the pixel
geometry — same rooms, same arrangement, same doors and windows as the
sketch, but every room set to the size actually written on it.

This is the right call for the stated purpose: the tool exists to answer
"will this 200 cm sofa fit", and tracing a 20% vertical error would give
confidently wrong answers. The apartment layout itself is unchanged.

If the drawn proportions are ever wanted instead, only the `ROOMS` array in
`planner.html` needs editing — nothing else depends on it.

**Worth confirming:** the labels should be checked against a tape measure in
the flat, particularly the vertical (north–south) ones, since those are the
dimensions the sketch draws least accurately.

---

## 11. Status

Built as `planner.html` — a single standalone file. Open it by
double-clicking; no server, no install, works offline.

All five phases are implemented: wall model, catalogue and drag-drop,
measurement layer, print/export, and save/load.

Verified in Chrome: rendering, placement, wall snapping, rotation, room
detection, door-swing clearance warnings, shopping-list grouping, and PNG
export.

### Known rough edges

- Room names are placeholders (Reception, Bedroom 1/2, Master Bed…) — rename
  by editing the `name` fields in `ROOMS`.
- Door and window positions along each wall are estimated from the sketch;
  their openings are visible in the drawing but not dimensioned.
- The corridor is modelled as one 100 cm strip spanning the flat. The sketch
  shows a slightly less regular shape.
- The terrace and balcony are approximate — their dimension labels (5.81,
  3.10, 1.10, 2.00) are used, but how they wrap the south-east corner is a
  reading of the sketch.


---

## 12. How much can the dimensions be trusted?

**Not as much as the plan's shape.** Measured against the sketch's own labels:

| Room | Traced (cm) | Sketch says | Error |
|---|---|---|---|
| Reception | 362 x 356 | 360 x 373 | +0% w, −4% h |
| Bedroom 1 | 359 x 356 | 360 x 348 | −0% w, +2% h |
| Bedroom 2 | 337 x 356 | 350 x 348 | −4% w, +2% h |
| Bathroom | 147 x 214 | 142 x 220 | +4% w, −3% h |
| Store | 209 x 120 | 206 x 132 | +1% w, −9% h |
| Toilet | 147 x 249 | 160 x 232 | −8% w, +7% h |
| Kitchen | 337 x 249 | 335 x 232 | +1% w, +7% h |
| Balcony | 92 x 195 | 110 x 200 | −16% w, −3% h |
| Corridor | 863 x 80 | — x 100 | −20% h |

(The Master Bedroom is L-shaped, so its two parts cannot be compared
against a single 3.60 x 5.10 label.)

### Three reasons not to treat these as exact

1. **The calibration is fitted to the labels, not independent.** The per-axis
   scale was chosen as the median of label/pixel ratios, so rooms landing
   near their labels is partly circular. It proves consistency, not accuracy.
2. **The sketch contradicts itself.** The same drawn length is labelled 3.73
   in one room and 3.48 in another. No scale can satisfy both, so the drawing
   is only good to roughly ±10%.
3. **The labels themselves are unverified.** Nobody has checked them against
   the actual flat.

### What that means in practice

±10% on a 3.5 m wall is **±35 cm**. That is the difference between a 2 m sofa
fitting a wall and not fitting it.

**Use the plan for layout, and a tape measure for commitment.** Before buying
anything expensive, measure the specific wall it goes against. The worst
offenders to re-measure first are the **corridor width** (−20%) and the
**balcony** (−16%).

---

## 13. Refinement pass

The first trace rendered 344 ragged rectangles with black blobs floating
inside the rooms. Cause: morphological closing merged adjacent bold digits
("3.60", "3.48") into single blobs large enough to pass the size filter.

Diagnosis: the real walls form **one connected component of 90,165 px** (plus
3,966 px for the entrance lobby). Every text blob is under 1,000 px. Raising
the component threshold to 1,500 px removes all text and keeps every wall.

Then wall-rectangle edges are snapped to clustered coordinates (66 distinct x
positions, 37 y) so lines are straight rather than pixel-ragged. Snapping is
non-destructive: any rectangle it would collapse keeps its original edges.
Result: 255 clean rectangles, no debris, no missing walls.

### Known remaining gaps

- **No door swing arcs.** They are thin single lines, so the thickness filter
  drops them with the dimension lines. Door *openings* are correct and
  visible; the swing clearance check is gone.
- **Room names are chosen, not derived.** The drawing does not label them.
- The balcony label crowds its wall - the room is narrower than the text.
