# `.floorplan.json` document format

Everything is **centimetres**. Origin is top-left, x runs right, y runs down —
so a wall from `(0,0)` to `(360,0)` is 3.60 m running east along the top.

```jsonc
{
  "version": 3,
  "name": "Flat — option A",
  "nextId": 42,                       // bump when you mint an id
  "ceiling": 280,                     // optional, used by the 3D view

  "underlay": {                       // the traced photo behind the drawing
    "src": "data:image/jpeg;base64,…",
    "x": 0, "y": 0,                   // where its top-left corner sits, in cm
    "cmPerPx": 1.44,                  // one image pixel = this many cm
    "w": 1354, "h": 936,              // the image's own pixel size
    "opacity": 0.45, "locked": true, "visible": true
  },

  "walls": [
    { "id": "w1", "x1": 0, "y1": 0, "x2": 360, "y2": 0, "t": 12 }
  ],

  "openings": [                       // doors and windows, BOUND TO A WALL
    { "id": "o1", "wall": "w1",
      "at": 135,                      // cm from that wall's (x1,y1) end
      "w": 90,                        // width of the hole
      "type": "door",                 // door | window | opening
      "style": "single",              // single | double | sliding | folding
      "hinge": 0,                     // 0 = hinged at the `at` end, 1 = far end
      "swing": 1 }                    // 1 or -1: which side the leaf opens
  ],

  "rooms": [
    { "id": "r1", "name": "Living",
      "kind": "indoor",               // indoor | balcony | outdoor | wet
      "poly": [[6,6],[414,6],[414,354],[6,354]],
      "color": null }
  ],

  "items": [                          // furniture
    { "id": "i1", "name": "Sofa 3-seat",
      "w": 200, "d": 90,              // real size; x,y is the CENTRE
      "x": 206, "y": 51,
      "rot": 0,                       // 0 | 90 | 180 | 270
      "shape": "rect",                // rect | circle | L
      "color": "#4f83cc",
      "fx": false, "fy": false,       // mirrored horizontally / vertically
      "note": "", "price": "" }
  ],

  "elec": [                           // electrical points
    { "id": "e1", "kind": "ceiling",  // see catalog.json -> electrical
      "x": 210, "y": 180, "rot": 0,
      "circuit": "c1",                // id of a circuit, or null
      "mount": null,                  // cm above floor; null = at ceiling
      "wall": "w3",                   // set when it snapped to a wall
      "note": "" }
  ],
  "circuits": [ { "id": "c1", "name": "L1", "color": "#c2410c" } ],

  "texts": [ { "id":"t1","x":60,"y":60,"text":"TV wall","size":26,"rot":0 } ],
  "dims":  [ { "id":"d1","x1":0,"y1":0,"x2":360,"y2":0,"off":-40 } ],
  "notes": [ { "id":"n1","x":100,"y":100,"tx":160,"ty":60,"text":"check this" } ]
}
```

## Things that catch people out

- **`x,y` on an item is its centre**, not a corner. A 200×90 sofa at
  `x:206, y:51` occupies x 106–306, y 6–96.
- **`rot: 90` swaps the footprint.** A 200×90 piece rotated 90° occupies
  90 wide × 200 deep. `w` and `d` themselves never change.
- **An opening belongs to its wall.** Move the wall and the door goes with it.
  `at` is measured from the wall's *first* end, so reversing a wall's
  endpoints moves every opening on it.
- **Room polygons are independent of walls.** They were traced from the walls
  when detected but are not re-derived, so moving a wall does not reshape a
  room. Re-detect in the editor if the walls change.
- **A design can legitimately have no rooms** — walls alone are valid. Room
  names, areas, the shopping list and the 3D floors all depend on rooms
  existing.
- **ids must be unique** across the whole document. Use `nextId` and increment.

## Rendering

Wall thickness `t` straddles the centre line: a wall with `t: 12` extends 6 cm
either side of the line from `(x1,y1)` to `(x2,y2)`. So a room's clear internal
size is the wall centre-line spacing minus one wall thickness.
