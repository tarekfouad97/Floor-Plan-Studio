"""
Convert the traced plan (plan.json, produced by walls2.py + emit.py) into the
document format editor.html saves and opens.

The trace stores walls as a raster decomposition - hundreds of little
rectangles. The editor wants centre-line SEGMENTS with a thickness, so each
rectangle becomes a segment along its long axis, then collinear neighbours
are merged back into single walls.

The original photo is embedded as the trace underlay so the drawn walls can
be checked against it. The trace is anisotropic (0.694 px/cm across,
0.780 down) but the editor's underlay has one scale, so the image is
resampled vertically to make a single scale correct on both axes.
"""
import json, base64, subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PX, PY = 0.694, 0.780          # px per cm, from emit.py

plan = json.load(open(os.path.join(ROOT, "plan.json")))
nid = [0]
def newid(p):
    nid[0] += 1
    return "%s%d" % (p, nid[0])

# ---------- 1. wall rectangles -> centre-line segments -------------------
segs = []
for x, y, w, h in plan["walls"]:
    if w <= 0 or h <= 0:
        continue
    if w >= h:                                   # horizontal
        segs.append(("H", round(y + h / 2, 1), round(x, 1), round(x + w, 1), round(h, 1)))
    else:                                        # vertical
        segs.append(("V", round(x + w / 2, 1), round(y, 1), round(y + h, 1), round(w, 1)))

# merge collinear, overlapping-or-touching runs of similar thickness
def merge(segs):
    buckets = {}
    for ax, c, a, b, t in segs:
        if t < 7: continue                      # hairline artefact, not a wall
        buckets.setdefault((ax, round(c / 9) * 9), []).append((a, b, c, t))
    out = []
    for (ax, _), rows in buckets.items():
        rows.sort()
        cur = None
        for a, b, c, t in rows:
            if cur and a <= cur[1] + 12:
                cur = (cur[0], max(cur[1], b), (cur[2] + c) / 2, max(cur[3], t))
            else:
                if cur: out.append((ax,) + cur)
                cur = (a, b, c, t)
        if cur: out.append((ax,) + cur)
    return out

merged = [s for s in merge(segs) if s[2] - s[1] >= 30]      # drop specks

walls = []
for ax, a, b, c, t in merged:
    c = round(c, 1); t = max(6.0, round(t, 1))
    if ax == "H": walls.append(dict(id=newid("w"), x1=round(a,1), y1=c, x2=round(b,1), y2=c, t=t))
    else:         walls.append(dict(id=newid("w"), x1=c, y1=round(a,1), x2=c, y2=round(b,1), t=t))

# ---------- 2. room rectangles -> polygons -------------------------------
def rects_to_poly(rects):
    """Exact outline of a union of axis-aligned rectangles."""
    if len(rects) == 1:
        x, y, w, h = rects[0]
        return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
    xs = sorted({v for x, y, w, h in rects for v in (x, x + w)})
    ys = sorted({v for x, y, w, h in rects for v in (y, y + h)})
    inside = lambda cx, cy: any(x <= cx <= x + w and y <= cy <= y + h for x, y, w, h in rects)
    occ = [[inside((xs[i] + xs[i+1]) / 2, (ys[j] + ys[j+1]) / 2)
            for j in range(len(ys) - 1)] for i in range(len(xs) - 1)]
    # collect boundary edges, then stitch them into a loop
    edges = {}
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            if not occ[i][j]: continue
            x0, x1c, y0, y1c = xs[i], xs[i+1], ys[j], ys[j+1]
            if j == 0 or not occ[i][j-1]: edges[(x0, y0)] = (x1c, y0)
            if j == len(ys) - 2 or not occ[i][j+1]: edges[(x1c, y1c)] = (x0, y1c)
            if i == 0 or not occ[i-1][j]: edges[(x0, y1c)] = (x0, y0)
            if i == len(xs) - 2 or not occ[i+1][j]: edges[(x1c, y0)] = (x1c, y1c)
    if not edges: return None
    start = next(iter(edges)); poly = [list(start)]; cur = edges[start]
    while tuple(cur) != start and len(poly) < 400:
        poly.append(list(cur)); cur = edges.get(tuple(cur))
        if cur is None: break
    # drop collinear points
    out = []
    for i, p in enumerate(poly):
        a, b = poly[i-1], poly[(i+1) % len(poly)]
        if (a[0] == p[0] == b[0]) or (a[1] == p[1] == b[1]): continue
        out.append(p)
    return out or poly

KIND = {"Balcony": "balcony", "Bathroom": "wet", "Toilet": "wet", "Kitchen": "wet"}
rooms = []
for r in plan["rooms"]:
    poly = rects_to_poly([list(map(float, q)) for q in r["rects"]])
    if not poly: continue
    rooms.append(dict(id=newid("r"), name=r["name"],
                      poly=[[round(p[0],1), round(p[1],1)] for p in poly],
                      kind=KIND.get(r["name"], "indoor"), color=None))

def _pt_in(x, y, poly):
    inside = False; n = len(poly); j = n - 1
    for i in range(n):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
            inside = not inside
        j = i
    return inside

# ---------- 3. openings: collinear gaps in a wall line -------------------
openings = []
lines = {}
for w in walls:
    horiz = abs(w["y2"] - w["y1"]) < 1
    key = ("H", round(w["y1"] / 4) * 4) if horiz else ("V", round(w["x1"] / 4) * 4)
    lines.setdefault(key, []).append(w)
for (ax, _), ws in lines.items():
    ws.sort(key=lambda w: w["x1"] if ax == "H" else w["y1"])
    for A, B in zip(ws, ws[1:]):
        aEnd = A["x2"] if ax == "H" else A["y2"]
        bBeg = B["x1"] if ax == "H" else B["y1"]
        gap = bBeg - aEnd
        if not (45 <= gap <= 200): continue
        mid = (aEnd + bBeg) / 2
        cross = A["y1"] if ax == "H" else A["x1"]
        # inside a room on both sides -> a door; otherwise it faces outside -> a window
        def inroom(px, py):
            return any(_pt_in(px, py, r["poly"]) for r in rooms)
        if ax == "H": s1, s2 = inroom(mid, cross - 45), inroom(mid, cross + 45)
        else:         s1, s2 = inroom(cross - 45, mid), inroom(cross + 45, mid)
        typ = "door" if (s1 and s2) else ("window" if (s1 or s2) else None)
        if typ is None: continue
        openings.append(dict(id=newid("o"), wall=A["id"],
                             at=round(aEnd - (A["x1"] if ax == "H" else A["y1"]), 1),
                             w=round(gap, 1), type=typ, hinge=0, swing=1,
                             **({"style": "single"} if typ == "door" else {})))

# ---------- 4. the photo as a pre-calibrated underlay --------------------
src_img = os.path.join(ROOT, "IMG_1933.jpeg")
tmp = "/tmp/underlay-corrected.jpg"
# squash vertically so ONE scale is correct on both axes
newh = int(round(936 * (PX / PY)))
subprocess.run(["sips", "--resampleHeightWidth", str(newh), "1354", src_img, "--out", tmp],
               capture_output=True)
b64 = base64.b64encode(open(tmp, "rb").read()).decode()
cmPerPx = 1.0 / PX
underlay = dict(src="data:image/jpeg;base64," + b64, w=1354, h=newh,
                x=round(-101 / PX, 1), y=round(-112 / PY, 1),
                cmPerPx=round(cmPerPx, 4), opacity=0.35, locked=True, visible=True)

DOC = dict(version=3, name="Flat — traced from sketch", nextId=nid[0] + 1,
           underlay=underlay, walls=walls, openings=openings, rooms=rooms,
           items=[], texts=[], dims=[], notes=[])
out = os.path.join(ROOT, "flat-traced.floorplan.json")
json.dump(DOC, open(out, "w"))
kb = os.path.getsize(out) // 1024
print("walls   %3d segments (from %d raster rectangles)" % (len(walls), len(plan["walls"])))
print("rooms   %3d polygons" % len(rooms))
for r in rooms:
    print("        %-12s %d points" % (r["name"], len(r["poly"])))
print("openings %2d  (%d doors, %d windows)" % (len(openings),
      sum(1 for o in openings if o["type"] == "door"),
      sum(1 for o in openings if o["type"] == "window")))
print("underlay resampled to 1354 x %d, one scale = %.4f cm/px" % (newh, cmPerPx))
print("wrote %s  (%d KB)" % (out, kb))
