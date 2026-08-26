---
name: interior-design
description: Furnish and lay out rooms in the apartment planner, check clearances, plan lighting and sockets, and show the result as a drawing inside the chat. Use whenever the user asks to furnish a room, suggest or improve a furniture layout, fit something into a space, plan electrics, or preview/see a .floorplan.json design.
---

# Interior design with the apartment planner

The user draws their flat in `editor.html` and saves `.floorplan.json` files.
This skill works on those files directly: read a design, lay furniture out,
verify it, and render a drawing to show in the chat.

## The three scripts

All live in `scripts/` next to this file. Run them with `python3`; they need
nothing installed.

| Script | Does |
|---|---|
| `render.py DESIGN.json [-o OUT.svg] [--room NAME]` | draws the plan to SVG |
| `check.py DESIGN.json [--room NAME] [--json]` | clearance / clash / circuit checks |
| `place.py DESIGN.json add\|elec\|clear\|list …` | edits the design |

`reference/catalog.json` holds the 113 furniture items with their real sizes,
plus the 24 electrical point types. **Always take sizes from there** rather
than inventing them — they are the same numbers the editor uses.

## How to work

1. **Read the design first.** `place.py DESIGN.json list` shows what is
   already there and which room each piece is in. Check what rooms exist and
   how big they are before proposing anything.
2. **Place furniture** with `place.py add`. Prefer `--room NAME --wall N|S|E|W
   --along CM`, which sets a piece flat against that side of the room — that
   is how furniture actually sits. Use `--at x,y` only for free-standing
   pieces like a coffee table or dining set.
3. **Run `check.py` after every change.** It catches furniture through walls,
   blocked door swings, overlaps, walkways under 75 cm, and lights on no
   circuit. Do not present a layout that still reports issues — fix them and
   re-run until it says OK, or explain any you deliberately accepted.
4. **Render and show it.** `render.py` writes an SVG; send it to the user with
   the file tool and `display: "render"` so the drawing appears in the chat.
   Use `--room NAME` for a close-up of one room.
5. **Say what changed and why** — in centimetres, referring to real walls and
   doors. "Sofa against the north wall, 85 cm clear to the coffee table" is
   useful; "cosy arrangement" is not.

## Laying out a room well

- **Circulation first.** Keep a walking route of at least 75 cm; 90 cm where
  people pass often. `check.py` enforces 75.
- **Anchor to the long wall.** Sofas, beds and wardrobes go flat against the
  longest uninterrupted wall, away from door swings.
- **Bed clearance.** At least 60 cm down one side to get in, 70 cm in front of
  a wardrobe to open it, 90 cm in front of a chest of drawers.
- **Seating distance.** Sofa to TV roughly 2.5–3× the screen width; coffee
  table 40–45 cm from the sofa front.
- **Dining.** 100 cm clear around a table so chairs pull out; 60 cm of table
  edge per person.
- **Never block** a door swing, a window opening, or a radiator.
- Check the room's real size before suggesting anything — a 200 cm sofa does
  not belong in a 250 cm wide room.

## Electrics

- `place.py elec KIND --room NAME [--wall N|S|E|W --along CM] --circuit NAME`.
- A **circuit** ties a switch to the lights it controls. Give both the same
  `--circuit` name and the editor draws the link.
- Sensible defaults, which the catalogue already carries: switches 110 cm,
  sockets 30 cm, worktop sockets 110 cm, A/C 220 cm.
- Put the switch by the door on the handle side, not the hinge side.
- Sockets: at least two per wall in a living room, one per 4 m of wall
  elsewhere, and a double beside the bed on each side.
- `check.py` flags a light on no circuit and a circuit with no switch.

## Rules

- **Centimetres, always.** Every coordinate and size in the document is cm.
- **Never invent a size.** Look it up in `reference/catalog.json`. If the user
  has a real piece with real dimensions, pass `-W` and `-D` to override.
- **Work on a copy** unless the user says to edit their file. Copy the design,
  edit that, and tell them the path.
- **Don't touch walls, rooms or openings** from this skill — those are the
  user's drawing. This skill furnishes; the editor draws.
- If a design has **no rooms**, say so: furniture can still be placed by
  coordinate, but room names, areas and the shopping list will be empty. Tell
  the user to press `R` in the editor and click inside each enclosed space.

## Reference

- `reference/document-format.md` — the full document schema.
- `reference/catalog.json` — furniture sizes, categories, electrical types.
