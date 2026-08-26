#!/usr/bin/env python3
"""
Check a .floorplan.json layout the way the editor does, so a layout can be
verified without opening a browser.

    python3 check.py DESIGN.json [--room NAME] [--json]

Reports: furniture through walls, blocked door swings, overlapping pieces,
walkways under 75 cm, items outside every room, and electrical circuits that
have no switch or no light.
"""
import json, argparse, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ELEC = {e["k"]: e for e in json.load(
    open(os.path.join(HERE, "..", "reference", "catalog.json")))["electrical"]}
WALK = 75


def wall_len(w): return math.hypot(w["x2"] - w["x1"], w["y2"] - w["y1"])
def wall_dir(w):
    L = wall_len(w) or 1
    return (w["x2"] - w["x1"]) / L, (w["y2"] - w["y1"]) / L, L
def wall_pt(w, at):
    ux, uy, _ = wall_dir(w)
    return w["x1"] + ux * at, w["y1"] + uy * at


def item_box(it):
    r = int(it.get("rot", 0)) % 360
    swap = r in (90, 270)
    w = it["d"] if swap else it["w"]
    h = it["w"] if swap else it["d"]
    return {"x": it["x"] - w / 2, "y": it["y"] - h / 2, "w": w, "h": h}


def overlap(a, b):
    return (a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and
            a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"])


def shrink(b, m):
    return {"x": b["x"] + m, "y": b["y"] + m, "w": b["w"] - 2 * m, "h": b["h"] - 2 * m}


def pt_in(x, y, poly):
    inside = False
    n = len(poly); j = n - 1
    for i in range(n):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
            inside = not inside
        j = i
    return inside


def room_at(doc, x, y):
    for r in reversed(doc.get("rooms", [])):
        if pt_in(x, y, r["poly"]):
            return r
    return None


def swing_box(doc, o):
    if o.get("type") != "door":
        return None
    w = next((v for v in doc["walls"] if v["id"] == o["wall"]), None)
    if not w:
        return None
    ux, uy, _ = wall_dir(w)
    nx, ny = -uy, ux
    hx, hy = wall_pt(w, o["at"] + o["w"] if o.get("hinge") else o["at"])
    ox, oy = wall_pt(w, o["at"] if o.get("hinge") else o["at"] + o["w"])
    tx = hx + nx * o.get("swing", 1) * o["w"]
    ty = hy + ny * o.get("swing", 1) * o["w"]
    xs = [hx, tx, ox]; ys = [hy, ty, oy]
    return {"x": min(xs), "y": min(ys), "w": max(xs) - min(xs), "h": max(ys) - min(ys)}


def check(doc, only_room=None):
    out = []
    rooms = doc.get("rooms", [])
    items = doc.get("items", [])
    if only_room:
        tgt = next((r for r in rooms if r["name"].lower() == only_room.lower()), None)
        if not tgt:
            sys.exit("No room called %r" % only_room)
        items = [i for i in items if pt_in(i["x"], i["y"], tgt["poly"])]

    for it in items:
        b = item_box(it); bt = shrink(b, 2)
        if rooms and not room_at(doc, it["x"], it["y"]):
            out.append(("outside", "%s sits outside every room" % it["name"]))
        for w in doc.get("walls", []):
            ux, uy, _ = wall_dir(w)
            t = w.get("t", 12)
            wb = {"x": min(w["x1"], w["x2"]) - abs(uy) * t / 2,
                  "y": min(w["y1"], w["y2"]) - abs(ux) * t / 2,
                  "w": abs(w["x2"] - w["x1"]) + abs(uy) * t,
                  "h": abs(w["y2"] - w["y1"]) + abs(ux) * t}
            if overlap(bt, wb):
                out.append(("wall", "%s runs into a wall" % it["name"]))
                break
        for o in doc.get("openings", []):
            sb = swing_box(doc, o)
            if sb and overlap(bt, sb):
                out.append(("door", "%s blocks a door swing" % it["name"]))
                break

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, c = items[i], items[j]
            if a["name"].startswith("Rug") or c["name"].startswith("Rug"):
                continue
            A, B = item_box(a), item_box(c)
            if overlap(shrink(A, 2), shrink(B, 2)):
                out.append(("overlap", "%s overlaps %s" % (a["name"], c["name"])))
                continue
            gx = max(A["x"] - (B["x"] + B["w"]), B["x"] - (A["x"] + A["w"]))
            gy = max(A["y"] - (B["y"] + B["h"]), B["y"] - (A["y"] + A["h"]))
            yov = min(A["y"] + A["h"], B["y"] + B["h"]) - max(A["y"], B["y"])
            xov = min(A["x"] + A["w"], B["x"] + B["w"]) - max(A["x"], B["x"])
            if 0 < gx < WALK and yov > 40 and gy < 0:
                out.append(("walkway", "only %d cm to walk between %s and %s"
                            % (round(gx), a["name"], c["name"])))
            elif 0 < gy < WALK and xov > 40 and gx < 0:
                out.append(("walkway", "only %d cm to walk between %s and %s"
                            % (round(gy), a["name"], c["name"])))

    circuits = {c["id"]: c for c in doc.get("circuits", [])}
    for e in doc.get("elec", []):
        d = ELEC.get(e["kind"])
        if not d:
            continue
        if d.get("load") == "light" and not e.get("circuit"):
            out.append(("circuit", "a %s is on no circuit" % d["name"]))
        if d.get("load") == "switch" and not e.get("circuit"):
            out.append(("circuit", "a %s controls nothing" % d["name"]))
    for cid, c in circuits.items():
        on = [e for e in doc.get("elec", []) if e.get("circuit") == cid]
        if not on:
            continue
        if not any(ELEC.get(e["kind"], {}).get("load") == "switch" for e in on):
            out.append(("circuit", "circuit %s has no switch" % c["name"]))
        if not any(ELEC.get(e["kind"], {}).get("load") == "light" for e in on):
            out.append(("circuit", "circuit %s has no light" % c["name"]))

    seen = set(); uniq = []
    for k, m in out:
        if m not in seen:
            seen.add(m); uniq.append((k, m))
    return uniq


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("design")
    ap.add_argument("--room", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    doc = json.load(open(a.design))
    res = check(doc, a.room)
    if a.json:
        print(json.dumps([{"kind": k, "message": m} for k, m in res], indent=1))
    elif not res:
        print("OK - nothing fouling walls, doors or walkways.")
    else:
        for k, m in res:
            print("[%-8s] %s" % (k, m))
        print("\n%d issue(s)." % len(res))
