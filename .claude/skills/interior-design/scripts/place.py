#!/usr/bin/env python3
"""
Add, move or clear furniture and electrical points in a .floorplan.json.

    # add furniture (sizes come from the catalogue; W/D can be overridden)
    python3 place.py DESIGN.json add "Sofa 3-seat" --at 240,80 --rot 0
    python3 place.py DESIGN.json add "Wardrobe 3-door" --at 100,300 --rot 90 --note "beige"

    # against a wall of a named room: --wall N|S|E|W --room "Living" --along 60
    python3 place.py DESIGN.json add "Sofa 3-seat" --room Living --wall N --along 120

    # electrical
    python3 place.py DESIGN.json elec ceiling --room Living --centre --circuit L1
    python3 place.py DESIGN.json elec switch1 --room Living --wall S --along 30 --circuit L1

    python3 place.py DESIGN.json clear --room Living      # remove that room's furniture
    python3 place.py DESIGN.json list                     # what's in the design

Writes in place unless -o is given. Always re-run check.py afterwards.
"""
import json, argparse, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CAT = json.load(open(os.path.join(HERE, "..", "reference", "catalog.json")))
BYNAME = {f["name"].lower(): f for f in CAT["furniture"]}
COLOR = {c["key"]: c["color"] for c in CAT["categories"]}
ELEC = {e["k"]: e for e in CAT["electrical"]}


def nid(doc, p):
    doc["nextId"] = doc.get("nextId", 1) + 1
    return "%s%d" % (p, doc["nextId"])


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


def find_room(doc, name):
    r = next((r for r in doc.get("rooms", []) if r["name"].lower() == name.lower()), None)
    if not r:
        sys.exit("No room %r. Rooms: %s"
                 % (name, ", ".join(x["name"] for x in doc.get("rooms", [])) or "(none)"))
    return r


def against_wall(room, side, along, w, d, rot):
    """Place a piece flat against one side of a room's bounding box."""
    x, y, rw, rh = bbox_of(room["poly"])
    swap = rot % 360 in (90, 270)
    ww, dd = (d, w) if swap else (w, d)
    side = side.upper()
    if side == "N":   return x + along + ww / 2, y + dd / 2
    if side == "S":   return x + along + ww / 2, y + rh - dd / 2
    if side == "W":   return x + dd / 2,        y + along + ww / 2
    if side == "E":   return x + rw - dd / 2,   y + along + ww / 2
    sys.exit("--wall must be N, S, E or W")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("design")
    ap.add_argument("cmd", choices=["add", "elec", "clear", "list"])
    ap.add_argument("what", nargs="?")
    ap.add_argument("--at", help="x,y in cm")
    ap.add_argument("--room"); ap.add_argument("--wall"); ap.add_argument("--along", type=float, default=0)
    ap.add_argument("--centre", action="store_true")
    ap.add_argument("--rot", type=int, default=0)
    ap.add_argument("-W", type=float); ap.add_argument("-D", type=float)
    ap.add_argument("--note", default=""); ap.add_argument("--price", default="")
    ap.add_argument("--circuit"); ap.add_argument("--mount", type=float)
    ap.add_argument("-o", "--out")
    a = ap.parse_args()

    doc = json.load(open(a.design))
    doc.setdefault("items", []); doc.setdefault("elec", []); doc.setdefault("circuits", [])

    if a.cmd == "list":
        print("%-22s %-12s %s" % ("ITEM", "ROOM", "SIZE"))
        for it in doc["items"]:
            rm = next((r["name"] for r in doc.get("rooms", [])
                       if pt_in(it["x"], it["y"], r["poly"])), "-")
            print("%-22s %-12s %d×%d @%d,%d rot%d"
                  % (it["name"], rm, it["w"], it["d"], it["x"], it["y"], it.get("rot", 0)))
        for e in doc["elec"]:
            c = next((c["name"] for c in doc["circuits"] if c["id"] == e.get("circuit")), "-")
            print("%-22s %-12s circuit %s" % (ELEC.get(e["kind"], {}).get("name", e["kind"]),
                                              "-", c))
        return

    if a.cmd == "clear":
        if not a.room:
            sys.exit("clear needs --room")
        r = find_room(doc, a.room)
        n0 = len(doc["items"])
        doc["items"] = [i for i in doc["items"] if not pt_in(i["x"], i["y"], r["poly"])]
        print("removed %d item(s) from %s" % (n0 - len(doc["items"]), r["name"]))

    elif a.cmd == "add":
        f = BYNAME.get((a.what or "").lower())
        if not f:
            sys.exit("Unknown item %r. Try: %s" % (a.what,
                     ", ".join(sorted(x["name"] for x in CAT["furniture"])[:8]) + " ..."))
        w = a.W or f["w"]; d = a.D or f["d"]
        if a.at:
            x, y = [float(v) for v in a.at.split(",")]
        elif a.room and a.wall:
            x, y = against_wall(find_room(doc, a.room), a.wall, a.along, w, d, a.rot)
        elif a.room:
            bx, by, bw, bh = bbox_of(find_room(doc, a.room)["poly"])
            x, y = bx + bw / 2, by + bh / 2
        else:
            sys.exit("give --at x,y or --room [--wall N|S|E|W --along cm]")
        it = {"id": nid(doc, "i"), "catalogId": None, "name": f["name"],
              "color": COLOR.get(f["cat"], "#4f83cc"), "shape": f.get("shape", "rect"),
              "w": w, "d": d, "x": round(x, 1), "y": round(y, 1), "rot": a.rot,
              "note": a.note, "price": a.price}
        doc["items"].append(it)
        print("added %s %d×%d at %d,%d rot %d" % (f["name"], w, d, it["x"], it["y"], a.rot))

    elif a.cmd == "elec":
        d = ELEC.get(a.what)
        if not d:
            sys.exit("Unknown point %r. Try: %s" % (a.what, ", ".join(sorted(ELEC))))
        if a.at:
            x, y = [float(v) for v in a.at.split(",")]
        elif a.room and a.wall:
            x, y = against_wall(find_room(doc, a.room), a.wall, a.along, 10, 10, 0)
        elif a.room:
            bx, by, bw, bh = bbox_of(find_room(doc, a.room)["poly"])
            x, y = bx + bw / 2, by + bh / 2
        else:
            sys.exit("give --at x,y or --room")
        cid = None
        if a.circuit:
            c = next((c for c in doc["circuits"] if c["name"].lower() == a.circuit.lower()), None)
            if not c:
                pal = ["#c2410c", "#1f8a54", "#2f6fd0", "#7a67c8", "#c98a3a", "#3f9bb5"]
                c = {"id": nid(doc, "c"), "name": a.circuit,
                     "color": pal[len(doc["circuits"]) % len(pal)]}
                doc["circuits"].append(c)
                print("created circuit %s" % c["name"])
            cid = c["id"]
        e = {"id": nid(doc, "e"), "kind": a.what, "x": round(x, 1), "y": round(y, 1),
             "rot": 0, "circuit": cid,
             "mount": a.mount if a.mount is not None else d.get("mount"), "note": a.note}
        doc["elec"].append(e)
        print("added %s at %d,%d%s" % (d["name"], e["x"], e["y"],
                                       " on %s" % a.circuit if a.circuit else ""))

    out = a.out or a.design
    json.dump(doc, open(out, "w"))
    print("saved %s" % out)


if __name__ == "__main__":
    main()
