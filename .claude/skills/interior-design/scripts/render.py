#!/usr/bin/env python3
"""
Render a .floorplan.json design to SVG so it can be viewed inside Claude.

    python3 render.py DESIGN.json [-o OUT.svg] [--room NAME] [--no-elec]
                      [--no-furniture] [--width PX]

Everything is centimetres in the document; the SVG viewBox is set in cm and
scaled by the width, so the drawing is always true to scale.
"""
import json, argparse, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CAT = json.load(open(os.path.join(HERE, "..", "reference", "catalog.json")))
COLOR = {c["key"]: c["color"] for c in CAT["categories"]}
BYNAME = {f["name"]: f for f in CAT["furniture"]}
ELEC = {e["k"]: e for e in CAT["electrical"]}
ROOMFILL = {"indoor": "#ffffff", "balcony": "#eef4ea",
            "outdoor": "#f1f3f5", "wet": "#eaf2f7"}


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def wall_len(w):
    return math.hypot(w["x2"] - w["x1"], w["y2"] - w["y1"])


def wall_dir(w):
    L = wall_len(w) or 1
    return (w["x2"] - w["x1"]) / L, (w["y2"] - w["y1"]) / L, L


def wall_pt(w, at):
    ux, uy, _ = wall_dir(w)
    return w["x1"] + ux * at, w["y1"] + uy * at


def poly_area(p):
    a = 0.0
    for i in range(len(p)):
        j = (i - 1) % len(p)
        a += (p[j][0] + p[i][0]) * (p[j][1] - p[i][1])
    return abs(a / 2)


def bbox_of(poly):
    xs = [q[0] for q in poly]; ys = [q[1] for q in poly]
    return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)


def pt_in(x, y, poly):
    inside = False
    n = len(poly); j = n - 1
    for i in range(n):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
            inside = not inside
        j = i
    return inside


def item_box(it):
    r = int(it.get("rot", 0)) % 360
    swap = r in (90, 270)
    w = it["d"] if swap else it["w"]
    h = it["w"] if swap else it["d"]
    return it["x"] - w / 2, it["y"] - h / 2, w, h


def render(doc, out, only_room=None, show_elec=True, show_furniture=True, width=1500):
    walls = doc.get("walls", [])
    rooms = doc.get("rooms", [])
    items = doc.get("items", []) if show_furniture else []
    elec = doc.get("elec", []) if show_elec else []
    circuits = {c["id"]: c for c in doc.get("circuits", [])}

    if only_room:
        target = next((r for r in rooms if r["name"].lower() == only_room.lower()), None)
        if not target:
            sys.exit("No room called %r. Rooms: %s"
                     % (only_room, ", ".join(r["name"] for r in rooms)))
        x, y, w, h = bbox_of(target["poly"])
        clip = (x - 60, y - 60, w + 120, h + 120)
        rooms = [target]
        items = [i for i in items if pt_in(i["x"], i["y"], target["poly"])]
        elec = [e for e in elec if pt_in(e["x"], e["y"], target["poly"])]
    else:
        pts = [(w["x1"], w["y1"]) for w in walls] + [(w["x2"], w["y2"]) for w in walls]
        for r in rooms:
            pts += [tuple(q) for q in r["poly"]]
        if not pts:
            sys.exit("Nothing to draw.")
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        m = 70
        clip = (min(xs) - m, min(ys) - m,
                max(xs) - min(xs) + 2 * m, max(ys) - min(ys) + 2 * m)

    vx, vy, vw, vh = clip
    px_per_cm = width / vw
    height = int(vh * px_per_cm)
    k = 1 / px_per_cm                      # cm per screen pixel, for text sizing

    o = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
         'viewBox="%.1f %.1f %.1f %.1f">' % (width, height, vx, vy, vw, vh)]
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#ffffff"/>'
             % (vx, vy, vw, vh))

    # ---- rooms -----------------------------------------------------------
    for r in rooms:
        pts = " ".join("%.1f,%.1f" % (q[0], q[1]) for q in r["poly"])
        o.append('<polygon points="%s" fill="%s"/>'
                 % (pts, ROOMFILL.get(r.get("kind", "indoor"), "#fff")))

    # ---- walls -----------------------------------------------------------
    for w in walls:
        ux, uy, L = wall_dir(w)
        t = w.get("t", 12) / 2
        nx, ny = -uy * t, ux * t
        pts = [(w["x1"] + nx, w["y1"] + ny), (w["x2"] + nx, w["y2"] + ny),
               (w["x2"] - nx, w["y2"] - ny), (w["x1"] - nx, w["y1"] - ny)]
        o.append('<polygon points="%s" fill="#222a34"/>'
                 % " ".join("%.1f,%.1f" % p for p in pts))

    # ---- openings --------------------------------------------------------
    for op in doc.get("openings", []):
        w = next((v for v in walls if v["id"] == op["wall"]), None)
        if not w:
            continue
        ux, uy, L = wall_dir(w)
        nx, ny = -uy, ux
        ax, ay = wall_pt(w, op["at"])
        bx, by = wall_pt(w, op["at"] + op["w"])
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#ffffff" '
                 'stroke-width="%.1f"/>' % (ax, ay, bx, by, w.get("t", 12) + 1.2))
        if op["type"] == "window":
            for s in (-0.22, 0.22):
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" '
                         'stroke="#4a6fa5" stroke-width="2.4"/>'
                         % (ax + nx * s * w.get("t", 12), ay + ny * s * w.get("t", 12),
                            bx + nx * s * w.get("t", 12), by + ny * s * w.get("t", 12)))
        elif op["type"] == "door":
            style = op.get("style", "single")
            sw = op.get("swing", 1)

            def leaf(hx, hy, ox, oy, R):
                tx, ty = hx + nx * sw * R, hy + ny * sw * R
                cross = (ox - hx) * (ty - hy) - (oy - hy) * (tx - hx)
                o.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 %d %.1f %.1f" fill="none" '
                         'stroke="#9fb0c6" stroke-width="1.4" stroke-dasharray="7 5"/>'
                         % (ox, oy, R, R, 0 if cross > 0 else 1, tx, ty))
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#5b6a7c" '
                         'stroke-width="%.1f"/>' % (hx, hy, tx, ty,
                                                    max(3, w.get("t", 12) * 0.28)))
            if style == "double":
                mx, my = wall_pt(w, op["at"] + op["w"] / 2)
                leaf(ax, ay, mx, my, op["w"] / 2)
                leaf(bx, by, mx, my, op["w"] / 2)
            elif style == "sliding":
                ox_, oy_ = nx * sw * w.get("t", 12) * 0.55, ny * sw * w.get("t", 12) * 0.55
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#5b6a7c" '
                         'stroke-width="%.1f"/>' % (ax + ox_, ay + oy_, bx + ox_, by + oy_,
                                                    max(3, w.get("t", 12) * 0.28)))
            else:
                if op.get("hinge"):
                    leaf(bx, by, ax, ay, op["w"])
                else:
                    leaf(ax, ay, bx, by, op["w"])

    # ---- furniture -------------------------------------------------------
    for it in items:
        col = it.get("color") or COLOR.get("living", "#4f83cc")
        bx_, by_, bw, bh = item_box(it)
        rot = it.get("rot", 0)
        g = ('<g transform="translate(%.1f %.1f) rotate(%d)">' % (it["x"], it["y"], rot))
        hw, hd = it["w"] / 2, it["d"] / 2
        if it.get("shape") == "circle":
            g += ('<ellipse cx="0" cy="0" rx="%.1f" ry="%.1f" fill="%s33" stroke="%s" '
                  'stroke-width="1.6"/>' % (hw, hd, col, col))
        else:
            g += ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s33" '
                  'stroke="%s" stroke-width="1.6"/>' % (-hw, -hd, it["w"], it["d"], col, col))
            g += ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                  'stroke-width="2.5" opacity="0.75"/>' % (-hw, hd, hw, hd, col))
        f = max(9 * k, 7)
        tr = ' transform="rotate(-90)"' if rot in (90, 270) else ""
        g += ('<text x="0" y="%.1f" text-anchor="middle" font-size="%.1f" fill="#46515e" '
              'font-weight="600" font-family="sans-serif" paint-order="stroke" '
              'stroke="#fff" stroke-width="%.1f"%s>%s'
              '<tspan x="0" dy="%.1f" font-size="%.1f" font-weight="400" fill="#79838f">'
              '%d×%d cm</tspan></text>'
              % (-f * 0.1, f, 3.2 * k, tr, esc(it["name"]), f * 1.05, f * 0.86,
                 round(it["w"]), round(it["d"])))
        g += "</g>"
        o.append(g)

    # ---- electrical ------------------------------------------------------
    if elec:
        R = max(9, 11 * k)
        for e in elec:
            d = ELEC.get(e["kind"])
            if not d:
                continue
            c = circuits.get(e.get("circuit"))
            col = c["color"] if c else "#33404e"
            x, y = e["x"], e["y"]
            o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fff" opacity="0.8"/>'
                     % (x, y, R * 1.5))
            if d.get("load") == "light":
                o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                         'stroke-width="1.6"/>' % (x, y, R, col))
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                         'stroke-width="1.6"/>' % (x - R, y, x + R, y, col))
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                         'stroke-width="1.6"/>' % (x, y - R, x, y + R, col))
            elif d.get("load") == "switch":
                o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
                         % (x, y, R * 0.42, col))
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                         'stroke-width="1.6"/>' % (x, y - R * 0.3, x + R * 0.75,
                                                   y - R * 1.05, col))
            else:
                o.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f Z" fill="none" '
                         'stroke="%s" stroke-width="1.6"/>'
                         % (x - R, y, R, R, x + R, y, col))
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
                         'stroke-width="1.6"/>' % (x, y, x, y - R * 0.75, col))

    # ---- room labels last, so they sit on top ----------------------------
    for r in rooms:
        x, y, w, h = bbox_of(r["poly"])
        f = 15 * k
        if w < f * 4 or h < f * 2.4:
            continue
        cx, cy = x + w / 2, y + h / 2
        o.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="%.1f" '
                 'fill="#8d98a4" font-weight="700" font-family="sans-serif" '
                 'letter-spacing="%.1f" paint-order="stroke" stroke="#fff" '
                 'stroke-width="%.1f">%s</text>'
                 % (cx, cy - 3 * k, f, 0.6 * k, 3.5 * k, esc(r["name"].upper())))
        o.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="%.1f" '
                 'fill="#b3bcc6" font-family="sans-serif" paint-order="stroke" '
                 'stroke="#fff" stroke-width="%.1f">%d × %d cm · %.1f m²</text>'
                 % (cx, cy + 13 * k, 12 * k, 3 * k, round(w), round(h),
                    poly_area(r["poly"]) / 10000))

    # ---- scale bar -------------------------------------------------------
    sx, sy = vx + 45, vy + vh - 40
    o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#6b7684" '
             'stroke-width="1.4"/>' % (sx, sy, sx + 500, sy))
    for i in range(6):
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#6b7684" '
                 'stroke-width="1.4"/>' % (sx + i * 100, sy - 5 * k, sx + i * 100, sy + 5 * k))
        o.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="%.1f" '
                 'fill="#7d8794" font-family="sans-serif">%d m</text>'
                 % (sx + i * 100, sy + 19 * k, 11 * k, i))
    o.append('<text x="%.1f" y="%.1f" font-size="%.1f" fill="#46515e" font-weight="700" '
             'font-family="sans-serif">%s</text>'
             % (vx + 45, vy + 40, 18 * k, esc(doc.get("name", "Floor plan"))))
    o.append("</svg>")

    open(out, "w").write("\n".join(o))
    return out, width, height


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("design")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--room", default=None, help="draw only this room, zoomed in")
    ap.add_argument("--no-elec", action="store_true")
    ap.add_argument("--no-furniture", action="store_true")
    ap.add_argument("--width", type=int, default=1500)
    a = ap.parse_args()
    doc = json.load(open(a.design))
    out = a.out or (os.path.splitext(a.design)[0] +
                    ("-%s" % a.room.lower().replace(" ", "-") if a.room else "") + ".svg")
    p, w, h = render(doc, out, a.room, not a.no_elec, not a.no_furniture, a.width)
    print("wrote %s  (%dx%d)" % (p, w, h))
