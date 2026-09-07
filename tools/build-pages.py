#!/usr/bin/env python3
"""Emit the guide pages for Floor Plan Studio.

Run once; the output is plain hand-editable HTML, committed to the repo. The
repo has no build step and this does not add one - it exists so the header,
footer and nav could not drift apart across six pages while I wrote them.

The furniture tables are generated from app.html's own CATALOG, so the
reference page and the planner can never disagree about a size.
"""
import io, json, os, re

ROOT = "/Users/tarekfouad/Desktop/sh2a"
BUILD = "2026-09-07.1"
SITE = "https://tarekfouad97.github.io/Floor-Plan-Studio"

MARK = ('<svg viewBox="0 0 32 32" fill="none" aria-hidden="true">'
  '<defs><linearGradient id="mk%s" x1="4" y1="2" x2="28" y2="20" gradientUnits="userSpaceOnUse">'
  '<stop stop-color="#7DD3FC"/><stop offset="1" stop-color="#818CF8"/></linearGradient></defs>'
  '<path d="M4 19.5 16 26 16 29 4 22.5Z" fill="#312E81"/>'
  '<path d="M28 19.5 16 26 16 29 28 22.5Z" fill="#3730A3"/>'
  '<path d="M16 13 28 19.5 16 26 4 19.5Z" fill="#4338CA"/>'
  '<path d="M4 10.5 16 17 16 20 4 13.5Z" fill="#4F46E5"/>'
  '<path d="M28 10.5 16 17 16 20 28 13.5Z" fill="#4338CA"/>'
  '<path d="M16 4 28 10.5 16 17 4 10.5Z" fill="url(#mk%s)"/></svg>')

FAV = ("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
  "<defs><linearGradient id='g' x1='4' y1='2' x2='28' y2='20' gradientUnits='userSpaceOnUse'>"
  "<stop stop-color='%237DD3FC'/><stop offset='1' stop-color='%23818CF8'/></linearGradient></defs>"
  "<path d='M4 19.5 16 26 16 29 4 22.5Z' fill='%23312E81'/>"
  "<path d='M28 19.5 16 26 16 29 28 22.5Z' fill='%233730A3'/>"
  "<path d='M16 13 28 19.5 16 26 4 19.5Z' fill='%234338CA'/>"
  "<path d='M4 10.5 16 17 16 20 4 13.5Z' fill='%234F46E5'/>"
  "<path d='M28 10.5 16 17 16 20 28 13.5Z' fill='%234338CA'/>"
  "<path d='M16 4 28 10.5 16 17 4 10.5Z' fill='url(%23g)'/></svg>")

NAV = [("guides.html", "Guides"), ("about.html", "About"), ("privacy.html", "Privacy")]


def head(page, title, desc, extra=""):
    nav = "".join(
        '\n      <a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == page else
                                          ('' if h != page else ''), t)
        for h, t in NAV)
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#05060A">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(site)s/%(page)s">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:type" content="article">
<meta property="og:url" content="%(site)s/%(page)s">
<meta name="twitter:card" content="summary">
<link rel="icon" href="%(fav)s">
<link rel="stylesheet" href="site.css">%(extra)s
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header>
  <div class="hbar">
    <a class="mark" href="index.html"><span class="tile">%(mark)s</span>Floor Plan Studio</a>
    <nav>%(nav)s
      <a class="btn" href="app.html?v=%(build)s">Open the planner</a>
    </nav>
  </div>
</header>
""" % dict(title=title, desc=desc, site=SITE, page=page, fav=FAV,
           mark=MARK % (0, 0), nav=nav, build=BUILD, extra=extra)


def foot(slot=None):
    ad = ""
    if slot:
        ad = """
<div class="wrap">
  <div class="adslot" data-ad-slot="%s" hidden>
    <span class="adlbl">Advertisement</span>
    <div class="adbox" data-note="%s &middot; responsive"></div>
  </div>
</div>
""" % (slot, slot)
    return ad + """
<footer>
  <div class="foot">
    <a class="mark" href="index.html" style="font-size:.96rem"><span class="tile">%(mark)s</span>Floor Plan Studio</a>
    <span class="sp"></span>
    <a href="guides.html">Guides</a>
    <a href="about.html">About</a>
    <a href="terms.html">Terms</a>
    <a href="privacy.html">Privacy</a>
    <a href="mailto:tare2fo2ad@gmail.com">Contact</a>
    <a href="app.html?v=%(build)s">Open the planner</a>
    <div class="fine">Free to use. The catalogue uses generic industry-standard
      sizes, not any one manufacturer&rsquo;s &mdash; measure the real thing before
      you buy it. Nothing here is architectural, structural or electrical advice.</div>
  </div>
</footer>
</body>
</html>
""" % dict(mark=MARK % (1, 1), build=BUILD)


def cards(items):
    out = ['<div class="cards">']
    for href, kicker, title, blurb in items:
        out.append('  <a href="%s"><span class="k">%s</span><h3>%s</h3><p>%s</p></a>'
                   % (href, kicker, title, blurb))
    out.append("</div>")
    return "\n".join(out)


def cta(title, body):
    return """
<div class="wrap">
  <div class="cta">
    <h2>%s</h2>
    <p>%s</p>
    <a class="btn btn-lg" href="app.html?v=%s">Open the planner &rarr;</a>
  </div>
</div>
""" % (title, body, BUILD)


def write(name, html):
    io.open(os.path.join(ROOT, name), "w", encoding="utf-8").write(html)
    print("wrote %-24s %6d bytes" % (name, len(html)))


# ---------------------------------------------------------------- catalogue
def catalogue():
    s = io.open(os.path.join(ROOT, "app.html"), encoding="utf-8").read()
    i = s.index("const CATALOG = [")
    j = s.index("\n];", i)
    rows = re.findall(r'\["(\w+)","([^"]+)",([\d.]+),([\d.]+)(?:,"(\w+)")?\]', s[i:j])
    cats = re.findall(r'\{ key:"(\w+)",\s*name:"([^"]+)"', s)
    by = {}
    for cat, name, w, d, shape in rows:
        by.setdefault(cat, []).append(
            dict(name=name, w=float(w), d=float(d), shape=shape or "rect"))
    return cats, by


def table(rows, caption):
    out = ['<div class="tw"><table>',
           '  <caption>%s</caption>' % caption,
           '  <thead><tr><th>Piece</th><th class="n">Width</th>'
           '<th class="n">Depth</th><th class="n">Footprint</th></tr></thead>',
           '  <tbody>']
    for r in rows:
        area = r["w"] * r["d"] / 10000.0
        out.append('    <tr><td>%s</td><td class="n">%g</td><td class="n">%g</td>'
                   '<td class="n">%.2f m&sup2;</td></tr>'
                   % (r["name"], r["w"], r["d"], area))
    out += ['  </tbody>', '</table></div>']
    return "\n".join(out)


# =========================================================== furniture sizes
NOTES = {
 "living": """<p>Almost everything you sit on in a living room has a seat height of
  <b>42&ndash;45&nbsp;cm</b>, and almost every sofa back reaches <b>80&ndash;90&nbsp;cm</b>.
  Coffee tables sit at <b>40&ndash;45&nbsp;cm</b>, roughly level with the sofa seat, which
  is why a taller dining-height table always looks wrong in front of one.</p>
  <p>The number that catches people out is <b>depth, not width</b>. A room will usually
  swallow a 240&nbsp;cm sofa; what it often cannot take is 95&nbsp;cm of depth plus the
  75&nbsp;cm of walkway that has to go behind it. Add the two together before you decide
  the wall is long enough.</p>""",

 "dining": """<p>Dining tables are <b>75&nbsp;cm</b> high almost without exception, and
  dining chair seats are <b>45&nbsp;cm</b>. That pairing is so standard that a table from
  one shop and chairs from another will nearly always work together.</p>
  <p>Allow <b>60&nbsp;cm of table edge per person</b> &mdash; so a 160&nbsp;cm table seats
  four comfortably and six at a squeeze. Round tables seat more people in less floor area
  than rectangular ones of the same width, and nobody gets a table leg between their
  knees.</p>""",

 "bedroom": """<p>Mattress sizes are fixed; bed <em>frames</em> are not. A frame adds
  <b>5&ndash;10&nbsp;cm</b> on each side and often 10&ndash;15&nbsp;cm at the foot, so a
  150&nbsp;cm king mattress can easily need 165&nbsp;cm of wall.</p>
  <p>Wardrobes are <b>60&nbsp;cm deep</b> because a coat hanger is 45&ndash;50&nbsp;cm
  across and needs clearance behind the door. Anything shallower has to hang its rail
  front-to-back, which halves what fits in it. Height runs 200&ndash;220&nbsp;cm &mdash;
  check that against your ceiling before you order, and check it against your
  <em>stairwell</em> before you order a rigid one.</p>""",

 "office": """<p>Desks are <b>73&ndash;75&nbsp;cm</b> high, matching dining tables.
  Depth matters more than people expect: <b>60&nbsp;cm</b> is the minimum, and
  <b>80&nbsp;cm</b> is what you want if a monitor is going to sit at a comfortable arm's
  length rather than in your face.</p>
  <p>The desk is never the problem. The chair is: it needs <b>90&ndash;110&nbsp;cm</b>
  behind the desk edge to push back and stand up, and that space cannot be shared with a
  walkway if anyone else uses the room.</p>""",

 "kitchen": """<p>Kitchens are the most standardised furniture in the house, which is
  what makes them plannable. Base units are <b>60&nbsp;cm deep and 87&nbsp;cm high</b>,
  plus a worktop of about 4&nbsp;cm, giving the familiar <b>91&nbsp;cm</b> working
  height. Wall units are <b>30&ndash;35&nbsp;cm deep</b>, hung 45&ndash;60&nbsp;cm above
  the worktop.</p>
  <p>Integrated appliance openings are <b>60&nbsp;cm wide</b> almost universally, with
  <b>45&nbsp;cm</b> for a slimline dishwasher. That means you can plan a kitchen in
  60&nbsp;cm units before you have chosen a single appliance, and it will still be right
  when you do.</p>""",

 "bath": """<p>A standard bath is <b>170&nbsp;&times;&nbsp;70&nbsp;cm</b>, and it is
  worth knowing that 1500 and 1600&nbsp;mm versions exist for small rooms. Shower trays
  come in 80&nbsp;&times;&nbsp;80, 90&nbsp;&times;&nbsp;90 and
  120&nbsp;&times;&nbsp;80&nbsp;cm.</p>
  <p>A WC projects about <b>70&nbsp;cm</b> from the wall and is 40&nbsp;cm wide, but the
  number that decides whether a bathroom works is the clear space <em>in front</em> of
  each fitting, not the fitting itself. Those figures are on the
  <a href="room-clearances.html">clearances page</a>.</p>""",

 "hall": """<p>Halls are narrow, so depth is everything. Shoe storage at
  <b>30&nbsp;cm</b> deep and a console table at <b>30&ndash;40&nbsp;cm</b> will pass in a
  corridor that a 45&nbsp;cm sideboard would block.</p>
  <p>A straight flight of stairs needs about <b>250&nbsp;cm</b> of floor run and
  <b>90&ndash;100&nbsp;cm</b> of width. That run is the single biggest thing most people
  forget when they redraw a hall.</p>""",
}

def page_furniture():
    cats, by = catalogue()
    n = sum(len(v) for v in by.values())
    body = []
    for key, label in cats:
        rows = sorted(by.get(key, []), key=lambda r: -r["w"] * r["d"])
        if not rows: continue
        body.append('<section id="%s" class="col">\n  <span class="ref">%s</span>\n'
                    '  <h2>%s sizes</h2>\n%s\n%s\n</section>'
                    % (key, label, label, NOTES.get(key, ""),
                       table(rows, "%s &mdash; %d pieces, width &times; depth in cm"
                             % (label, len(rows)))))
    toc = " &middot; ".join('<a href="#%s">%s</a>' % (k, l) for k, l in cats if by.get(k))

    return head("furniture-sizes.html",
        "Standard furniture sizes in cm — every piece, room by room",
        "Standard width and depth in centimetres for %d pieces of furniture, grouped by "
        "room, with the heights that go with them and the doorway measurements that decide "
        "whether it gets into the house at all." % n) + """
<div class="wrap head">
  <span class="eyebrow"><span class="dot"></span>Reference &middot; %(n)d pieces</span>
  <h1>Standard furniture sizes, in centimetres</h1>
  <p class="sum">Every piece in the planner&rsquo;s catalogue, at the size the trade
  actually builds it. Use these to lay a room out before you have chosen a single
  product &mdash; then measure the real thing before you buy it, because the shop&rsquo;s
  version will be a few centimetres different and a few centimetres is the whole
  game.</p>
  <p class="sum" style="font-size:.92rem">Jump to: %(toc)s</p>
</div>

<main id="main"><div class="wrap">

<section class="col">
  <span class="ref">How to use this</span>
  <h2>Read depth first, width second</h2>
  <p>Nearly everyone plans a room by asking whether a piece is <em>wide</em> enough to fit
  a wall. That is rarely what goes wrong. What goes wrong is depth: a sofa that is
  95&nbsp;cm deep has taken almost a metre out of the room before anyone has walked past
  it, and the walkway behind it needs another 75&nbsp;cm. One and a half metres of a
  3.5&nbsp;metre room, gone, to a piece you were thinking of as &ldquo;a two-metre
  sofa&rdquo;.</p>
  <p>So the useful sum is always <b>depth + clearance</b>, on every wall, before you
  worry about width. The figures for the clearance half are on the
  <a href="room-clearances.html">clearances page</a>.</p>
  <div class="note">These are generic industry-standard dimensions, not any one
  manufacturer&rsquo;s data. They exist so you can plan realistically before you have
  chosen a product. Every real piece varies by a few centimetres &mdash; and on the tight
  ones, that is the difference between fitting and not.</div>
</section>

<section class="col">
  <span class="ref">Before you buy</span>
  <h2>The doorway test</h2>
  <p>A sofa that fits your living room perfectly is still useless if it cannot get into
  the building. This is the most common expensive mistake in furniture buying, and it
  takes four measurements to avoid.</p>
  <ol>
    <li><b>The narrowest door on the route</b>, measured through the open frame, not the
      architrave. A UK internal door is usually 76&nbsp;cm (2&prime;6&Prime;) or
      83&nbsp;cm (2&prime;9&Prime;); front doors run 81&ndash;91&nbsp;cm.</li>
    <li><b>The door height</b>, usually 198&nbsp;cm.</li>
    <li><b>The hallway width</b> at the tightest point, and the width of any turn. A long
      piece has to pivot, and a 90&deg; turn in a 90&nbsp;cm corridor is much harder than
      the numbers suggest.</li>
    <li><b>The stairs</b> &mdash; width, and crucially the half-landing, where a rigid
      wardrobe will stop dead.</li>
  </ol>
  <p>Then the test itself. Big upholstery goes through a door <b>on its side</b>. So the
  piece&rsquo;s <em>depth</em> has to clear the door <em>width</em>, and the piece&rsquo;s
  <em>height</em> has to clear it too once it is tipped. A 90&nbsp;cm deep, 85&nbsp;cm
  high sofa will not pass a 76&nbsp;cm door in any orientation. A 76&nbsp;cm door takes a
  sofa up to about 75&nbsp;cm deep, and that is why so many sofas are built at exactly
  that depth.</p>
  <div class="note warn">If the numbers are close, check whether the feet unscrew and
  whether the back detaches &mdash; on many sofas both do, and that is often the ten
  centimetres you need.</div>
</section>

%(body)s

<section class="col">
  <span class="ref">Keep reading</span>
  <h2>The other half of the problem</h2>
  <p>Sizes tell you what a piece takes up. They do not tell you how much space has to be
  left around it, which is what actually decides whether a room is pleasant to live
  in.</p>
  %(cards)s
</section>

</div>

%(cta)s
</main>
""" % dict(n=n, toc=toc, body="\n\n".join(body),
           cards=cards([
             ("room-clearances.html", "Guide", "Clearances and walkways",
              "How much floor to leave in front of, behind and beside everything &mdash; "
              "with the figures the planner checks against."),
             ("measure-a-room.html", "Guide", "How to measure a room",
              "What to measure, in what order, and the six things people forget until "
              "the furniture is already in the van."),
           ]),
           cta=cta("Try it against your own room",
                   "Draw your walls to scale, drop these pieces in at their real sizes, "
                   "and see what is actually left.")) + foot("in-content-1")


# ============================================================== clearances
CLEAR = [
 ("Main walkway through a room", "90", "75", "Two people pass sideways at 90. At 75 one of you waits."),
 ("Secondary route, one person", "75", "60", "Below 60 you turn sideways every time."),
 ("Squeeze between furniture", "60", "50", "Fine occasionally. Miserable daily."),
 ("Dining table edge to wall", "100", "75", "100 lets someone walk behind a seated guest."),
 ("Beside a bed, main side", "75", "60", "60 is enough to get in. 75 is enough to make it."),
 ("Beside a bed, second side", "60", "40", "40 works if nobody sleeps that side."),
 ("Foot of the bed, if it is a route", "90", "75", "Less than 75 and you shuffle."),
 ("In front of a hinged wardrobe", "90", "75", "The door is ~50 cm. You are the rest."),
 ("In front of a chest of drawers", "90", "75", "A drawer pulls out about 50 cm."),
 ("Between opposite kitchen runs", "120", "100", "Under 100 and two people cannot pass. 90 is the floor."),
 ("In front of a single kitchen run", "100", "90", "Enough to open an oven and stand back."),
 ("Behind a desk chair", "110", "90", "To push back and stand without hitting a wall."),
 ("Sofa to coffee table", "45", "35", "Close enough to reach, far enough for legs."),
 ("In front of a WC", "60", "50", "Plus 20 cm each side of its centre line."),
 ("In front of a basin", "70", "55", "You lean forward at a basin, so it needs more than it looks."),
 ("At a shower or bath entry", "70", "55", "Enough to stand and dry off."),
 ("A door's swing", "80", "70", "A clear quarter circle of the door's own width."),
 ("Wheelchair turning circle", "150", "150", "A full 360. 120 does a three-point turn."),
]

def page_clearances():
    rows = "\n".join(
      '    <tr><td>%s</td><td class="n">%s</td><td class="n">%s</td><td>%s</td></tr>'
      % (a, b, c, d) for a, b, c, d in CLEAR)
    return head("room-clearances.html",
      "Room clearances and walkway widths, in cm — how much space to leave",
      "The gaps that decide whether a room works: walkways, space behind a dining chair, "
      "beside a bed, in front of a wardrobe and between kitchen runs. Comfortable and "
      "minimum figures in centimetres.") + """
<div class="wrap head">
  <span class="eyebrow"><span class="dot"></span>Reference &middot; clearances</span>
  <h1>How much space to leave around everything</h1>
  <p class="sum">Furniture sizes tell you what a room will hold. Clearances tell you
  whether living in it will be any good. These are the gaps &mdash; in centimetres
  &mdash; that decide whether you walk through a room or edge around it.</p>
</div>

<main id="main"><div class="wrap">

<section class="col">
  <span class="ref">The short version</span>
  <h2>Three numbers do most of the work</h2>
  <p>If you remember nothing else on this page, remember these. Almost every clearance
  problem in a home is one of them.</p>
  <ul>
    <li><b>90&nbsp;cm</b> &mdash; a route two people can use. Hallways, the main path
      through a living room, the gap between kitchen runs.</li>
    <li><b>75&nbsp;cm</b> &mdash; a route one person can use without thinking about it.
      This is the working minimum for anywhere you walk every day.</li>
    <li><b>60&nbsp;cm</b> &mdash; a squeeze. You will turn sideways. Acceptable for a
      spare room, a nuisance anywhere else.</li>
  </ul>
  <div class="note">Below 60&nbsp;cm you are not designing a walkway, you are designing
  an obstacle. The planner flags anything under 60 as a failure and anything between 60
  and 75 as tight.</div>
</section>

<section class="col">
  <span class="ref">The table</span>
  <h2>Every clearance worth knowing</h2>
  <p><b>Comfortable</b> is what to design for. <b>Minimum</b> is what you can live with
  when the room genuinely cannot give you more. Both in centimetres.</p>
  <div class="tw"><table>
  <caption>Clearances &mdash; centimetres of clear floor</caption>
  <thead><tr><th>Where</th><th class="n">Comfortable</th><th class="n">Minimum</th>
    <th>Why</th></tr></thead>
  <tbody>
%(rows)s
  </tbody>
  </table></div>
</section>

<section class="col">
  <span class="ref">Dining</span>
  <h2>The one everybody gets wrong</h2>
  <p>A dining table fits the room on paper and still traps everyone against the wall,
  because the table is not the thing that needs space &mdash; the <em>chair</em> is.</p>
  <p>A chair needs about <b>45&nbsp;cm</b> to pull out and be sat on. So a person sitting
  down has already used 45&nbsp;cm beyond the table edge before anyone tries to walk past
  them. Add a 75&nbsp;cm walkway behind that and you need <b>120&nbsp;cm from table edge
  to wall</b> for a room where people can circulate while others eat.</p>
  <p>The practical figures: <b>100&nbsp;cm</b> from table edge to wall is comfortable,
  <b>75&nbsp;cm</b> works but nobody passes behind an occupied chair, and under
  <b>75&nbsp;cm</b> the chair cannot pull out far enough to sit down properly. For a
  90&nbsp;cm deep table that means a room <b>290&nbsp;cm</b> deep to be comfortable and
  <b>240&nbsp;cm</b> to be workable.</p>
  <div class="note">There is a live version of this sum on the
  <a href="index.html#fit">home page</a> &mdash; drag the room depth and watch the
  walkway appear and disappear.</div>
</section>

<section class="col">
  <span class="ref">Bedrooms</span>
  <h2>Beds, and the side nobody uses</h2>
  <p>A double bed wants <b>75&nbsp;cm</b> down at least one side and <b>60&nbsp;cm</b>
  down the other. You can drop the second side to <b>40&nbsp;cm</b> if it is genuinely
  never used &mdash; against a wall, in a single room &mdash; but you will be changing
  the sheets from one side for the rest of your life.</p>
  <p>The foot of the bed only needs clearance if it is a route to somewhere. If it is,
  give it <b>75&nbsp;cm</b>. If the wardrobe is down there, give it <b>90&nbsp;cm</b>,
  because the wardrobe door needs its own swing before you even stand in front of it.</p>
</section>

<section class="col">
  <span class="ref">Kitchens</span>
  <h2>Two runs facing each other</h2>
  <p>A galley kitchen lives or dies on the gap between the two runs. <b>120&nbsp;cm</b>
  lets two people work at once and lets a dishwasher door open while somebody passes.
  <b>100&nbsp;cm</b> works for one cook. <b>90&nbsp;cm</b> is the absolute floor, and at
  90 an open oven door and an open fridge door will meet in the middle.</p>
  <p>Check the door swings, not just the gap. An oven door projects about
  <b>55&nbsp;cm</b>, a dishwasher about <b>60&nbsp;cm</b>, and a fridge door swung
  through 90&deg; projects its full depth of <b>60&nbsp;cm</b>. Those are the numbers
  that turn a 100&nbsp;cm gap into a 40&nbsp;cm gap while you are cooking.</p>
</section>

<section class="col">
  <span class="ref">Doors</span>
  <h2>The quarter circle nobody draws</h2>
  <p>A door needs a clear quarter circle with a radius of its own width &mdash; so a
  76&nbsp;cm door sweeps 76&nbsp;cm of floor, every time it opens. Nothing may live in
  that arc: not a bin, not a radiator, and certainly not the corner of a bed.</p>
  <p>This is the single most common thing a plan gets wrong, because a door is drawn as a
  line and its swing is invisible until you are standing in the room. Draw the arc. The
  planner draws it for you and warns when something is sitting in it.</p>
</section>

<section class="col">
  <span class="ref">Keep reading</span>
  <h2>Next</h2>
  %(cards)s
</section>

</div>

%(cta)s
</main>
""" % dict(rows=rows,
  cards=cards([
    ("furniture-sizes.html", "Reference", "Standard furniture sizes",
     "Width and depth in centimetres for 116 pieces, room by room, with the doorway "
     "test that decides whether it gets in at all."),
    ("measure-a-room.html", "Guide", "How to measure a room",
     "What to measure, in what order, and the six things people forget."),
  ]),
  cta=cta("Check your own clearances",
          "Draw the room, drop the furniture in, and the planner flags every walkway "
          "and door swing that does not work &mdash; while you are still moving things "
          "around.")) + foot("in-content-1")


# =========================================================== measure a room
def page_measure():
    return head("measure-a-room.html",
      "How to measure a room for furniture — a practical order of work",
      "What to measure and in what order, how to check a room is actually square, and "
      "the six things people forget until the furniture is already in the van.") + """
<div class="wrap head">
  <span class="eyebrow"><span class="dot"></span>Guide &middot; 10 minutes</span>
  <h1>How to measure a room properly</h1>
  <p class="sum">Ten minutes with a tape measure, done in the right order, is the
  difference between a plan you can trust and a plan that is quietly wrong by fifteen
  centimetres in the one place it matters.</p>
</div>

<main id="main"><div class="wrap">

<section class="col">
  <span class="ref">What you need</span>
  <h2>A tape, a pencil, and one sheet of paper</h2>
  <p>A <b>5&nbsp;metre tape measure</b> is enough for any normal room. A laser measure is
  faster and worth it if you are doing a whole flat, but it is not more accurate for
  anything at this scale &mdash; the errors that matter come from measuring the wrong
  thing, not from measuring it imprecisely.</p>
  <p>Sketch the room first, roughly, not to scale, before you measure anything. A rough
  outline with the doors and windows on it gives you somewhere to write numbers. Trying
  to draw and measure at the same time is how walls get missed.</p>
  <div class="note">Work in <b>centimetres</b> throughout and write the unit down every
  time. Mixing metres and millimetres on one sheet is the single most reliable way to
  order a worktop ten centimetres short.</div>
</section>

<section class="col">
  <span class="ref">The order</span>
  <h2>Measure in this order</h2>
  <ol>
    <li><b>Wall to wall, at floor level.</b> Skirting boards steal 1&ndash;2&nbsp;cm each
      side, and furniture sits against the skirting, not the wall. Measure the gap the
      furniture will actually occupy.</li>
    <li><b>Each wall separately, corner to corner.</b> Do not assume opposite walls
      match. In older buildings they routinely differ by several centimetres.</li>
    <li><b>Both diagonals.</b> If they are equal, the room is square. If they are not
      &mdash; and often they are not &mdash; you now know by how much, and you know not
      to trust a plan drawn as a neat rectangle.</li>
    <li><b>Ceiling height</b>, in two or three places. Floors slope. This decides whether
      a 220&nbsp;cm wardrobe goes in, and whether it can be tilted upright once it is
      inside.</li>
    <li><b>Every door:</b> the clear opening width, the height, which way it swings, and
      how far into the room it swings.</li>
    <li><b>Every window:</b> width, height, and &mdash; the one people miss &mdash; the
      height of the sill from the floor. That number decides whether a sofa back or a
      desk can sit under it.</li>
  </ol>
</section>

<section class="col">
  <span class="ref">The awkward bits</span>
  <h2>Six things people forget</h2>
  <ul>
    <li><b>Radiators.</b> Width, height, and how far they stand off the wall &mdash;
      usually 8&ndash;12&nbsp;cm. Furniture cannot sit flat against a wall with a
      radiator on it, and you should not box one in with a sofa anyway.</li>
    <li><b>Pipe boxing and soil stacks.</b> Usually a 20&ndash;30&nbsp;cm square in a
      corner. Small, and it will be exactly where you wanted the wardrobe.</li>
    <li><b>The window reveal.</b> How deep the window sits into the wall. Curtains,
      blinds and shutters all live in that depth.</li>
    <li><b>Sockets and switches.</b> Measure their height and position. Putting a
      sideboard over the only socket on that wall is a decision, not an accident, and you
      want to make it deliberately.</li>
    <li><b>Sloped ceilings.</b> Measure the height at the low point and how far in it
      reaches. A loft room's usable floor is much smaller than its actual floor.</li>
    <li><b>The route in.</b> Measure the front door, the hallway, the stairs and the
      half-landing while you have the tape out. This is the
      <a href="furniture-sizes.html">measurement that stops a sofa</a>, and it is the one
      nobody takes.</li>
  </ul>
</section>

<section class="col">
  <span class="ref">Getting it into a plan</span>
  <h2>Two ways to turn numbers into a drawing</h2>
  <p>If you already have a plan &mdash; an estate agent&rsquo;s brochure, an
  architect&rsquo;s drawing, even a photo of one &mdash; the fastest route is to
  <b>trace over it</b>. Load the image, tell the planner the real distance between two
  points on it so it knows the scale, and either draw over the top or let it find the
  walls for you.</p>
  <p>If you are starting from your own measurements, <b>draw the walls</b> and type each
  length as you go. Every number you type is real centimetres, so the plan is to scale
  from the first wall onwards, and you will see immediately if your diagonals were
  telling you the room is not square.</p>
  <p>Then put the furniture in at
  <a href="furniture-sizes.html">its real size</a> and check the
  <a href="room-clearances.html">clearances</a>. That is the whole job.</p>
</section>

<section class="col">
  <span class="ref">Keep reading</span>
  <h2>Next</h2>
  %(cards)s
</section>

</div>

%(cta)s
</main>
""" % dict(
  cards=cards([
    ("furniture-sizes.html", "Reference", "Standard furniture sizes",
     "116 pieces at industry-standard width and depth, room by room."),
    ("room-clearances.html", "Reference", "Clearances and walkways",
     "How much floor to leave around everything, with comfortable and minimum figures."),
  ]),
  cta=cta("You have the numbers. Draw it.",
          "Ten minutes to put your measurements on screen, and you will know what "
          "fits before you spend anything.")) + foot("in-content-1")


# ================================================================= guides hub
def page_guides():
    return head("guides.html",
      "Guides — furniture sizes, clearances and how to measure a room",
      "Practical reference for planning a room: standard furniture dimensions in "
      "centimetres, the clearances that make a layout work, and how to measure a room "
      "properly.") + """
<div class="wrap head">
  <span class="eyebrow"><span class="dot"></span>Three guides</span>
  <h1>Guides</h1>
  <p class="sum">Everything the planner knows about sizes and spacing, written down.
  These are the figures it checks your drawing against, so you can use them whether or
  not you ever open the tool.</p>
</div>

<main id="main"><div class="wrap">

<section class="col">
  <span class="ref">Start here</span>
  <h2>If you are about to buy something</h2>
  <p>Read the <a href="furniture-sizes.html">furniture sizes</a> page for what the piece
  takes up, then <a href="room-clearances.html">clearances</a> for what has to be left
  around it. Those two together answer almost every &ldquo;will it fit&rdquo;
  question.</p>
  <p>If you have not measured the room yet, start with
  <a href="measure-a-room.html">how to measure a room</a> &mdash; particularly the part
  about the route in, which is what actually stops sofas.</p>
  %(cards)s
</section>

<section class="col">
  <span class="ref">A note on the numbers</span>
  <h2>Where these figures come from</h2>
  <p>The furniture dimensions are generic industry-standard sizes &mdash; the sizes the
  trade builds to &mdash; not any one manufacturer&rsquo;s catalogue. They are the same
  numbers the planner draws with, generated from its own catalogue so the two can never
  disagree.</p>
  <p>The clearance figures are the long-established rules of thumb used in interior
  layout: the width a person needs to pass, the space a chair needs to pull out, the arc
  a door sweeps. They are guidance for planning a home, not building regulations. If you
  are doing work that needs to meet a standard &mdash; accessibility, fire escape routes,
  structural changes &mdash; get that from the regulations for your country and from
  someone qualified.</p>
  <div class="note">Always measure the actual product before you buy it. Every real piece
  differs from the standard by a few centimetres, and on the tight ones a few centimetres
  is the entire question.</div>
</section>

</div>

%(cta)s
</main>
""" % dict(
  cards=cards([
    ("furniture-sizes.html", "Reference", "Standard furniture sizes in cm",
     "116 pieces at their industry-standard width and depth, grouped by room, with "
     "typical heights and the doorway test."),
    ("room-clearances.html", "Reference", "Clearances and walkway widths",
     "How much clear floor to leave in front of, behind and beside everything &mdash; "
     "comfortable and minimum, in centimetres."),
    ("measure-a-room.html", "Guide", "How to measure a room",
     "A ten-minute order of work, how to check a room is square, and the six things "
     "people forget."),
    ("index.html#fit", "Try it", "The clearance demo",
     "Drag a room wider and narrower and watch the walkway behind a dining chair appear "
     "and disappear."),
  ]),
  cta=cta("Put it into practice",
          "Draw your room to scale, place real furniture, and let the planner do the "
          "checking.")) + foot("in-content-1")


# ===================================================================== about
def page_about():
    return head("about.html",
      "About Floor Plan Studio — who makes it and why it is free",
      "Floor Plan Studio is a free floor planner built by an independent developer. "
      "Here is who is behind it, why it exists, how it is paid for, and how to get in "
      "touch.") + """
<div class="wrap head">
  <span class="eyebrow"><span class="dot"></span>About</span>
  <h1>About Floor Plan Studio</h1>
  <p class="sum">A free floor planner for people with a tape measure and a nagging doubt
  about whether the sofa fits. No account, no paid tier, and nothing you draw leaves your
  browser.</p>
</div>

<main id="main"><div class="wrap">

<section class="col">
  <span class="ref">Who</span>
  <h2>Who makes it</h2>
  <p>Floor Plan Studio is built and maintained by <b>Tarek</b>, an independent developer,
  alongside a day job. It is not a company, it is not venture funded, and there is no
  team &mdash; which is why it does exactly one thing and tries to do it properly.</p>
  <p>You can reach me directly at
  <a href="mailto:tare2fo2ad@gmail.com">tare2fo2ad@gmail.com</a>. I read everything,
  including the bug reports, and particularly the ones that come with a saved
  <code>.json</code> file attached.</p>
</section>

<section class="col">
  <span class="ref">Why</span>
  <h2>Why it exists</h2>
  <p>It started with a flat and a sketch on A4. I wanted to know whether a particular
  sofa would work in a particular room, and every tool I tried wanted an account, wanted
  a subscription, or gave me a pretty 3D render that quietly refused to tell me the one
  number I actually needed &mdash; how many centimetres were left to walk through.</p>
  <p>So this one is built the other way round. The measurements come first. The 3D view
  is there because it helps you understand a space, not because it is the point. The
  point is the printed page you carry into a shop with every size on it.</p>
  <p>That is also why it is centimetres everywhere, with no unit switcher. Mixing metres
  and millimetres is how people end up ordering a worktop ten centimetres short, and one
  unit throughout removes an entire category of mistake.</p>
</section>

<section class="col">
  <span class="ref">How it works</span>
  <h2>How it is built</h2>
  <p>The planner is a single HTML file that runs entirely in your browser. There is no
  server, no database and no account system, so there is nowhere for your floor plans to
  go even if someone wanted them. Work in progress is saved in your own browser&rsquo;s
  storage; saving to a file puts a <code>.json</code> on your own machine that is yours
  to keep.</p>
  <p>The furniture catalogue uses generic industry-standard dimensions rather than any
  manufacturer&rsquo;s data, so there is nothing to license and nothing to go out of
  date. The <a href="guides.html">guides</a> publish those same numbers, generated from
  the catalogue itself.</p>
  <p>The full detail of what is and is not stored is in the
  <a href="privacy.html">privacy policy</a>, which is written to be read rather than to
  cover anybody.</p>
</section>

<section class="col">
  <span class="ref">Money</span>
  <h2>How it is paid for</h2>
  <p>It is free, and it is going to stay free. There is no paid tier, no trial that
  expires and no feature held back for a subscription.</p>
  <p>Hosting a single HTML file costs almost nothing, but a domain and the time to keep
  it working are not nothing. The plan is to carry a small number of ordinary display ads
  on the site &mdash; on these pages, never inside the planner itself, never as a pop-up
  or an overlay, and never anything that covers your drawing. If that ever stops being
  true, it will be because I have changed my mind, and the
  <a href="privacy.html">privacy policy</a> will say so before it happens rather than
  after.</p>
</section>

<section class="col">
  <span class="ref">Limits</span>
  <h2>What it is not</h2>
  <p>It is a planning tool for deciding what to buy and where it goes. It is not a
  substitute for an architect, a structural engineer or an electrician, and it does not
  produce a certified drawing. The electrical layer exists so you can mark up what you
  want and brief someone qualified &mdash; not so you can wire a house from it.</p>
  <p>The clearance figures in the guides are established rules of thumb for laying out a
  home. They are not building regulations, and they are not accessibility standards. If
  your work has to meet a standard, get that from the regulations where you live.</p>
</section>

</div>

%(cta)s
</main>
""" % dict(cta=cta("Have a look",
                   "It opens instantly and there is nothing to sign up for.")) + foot()


# ===================================================================== terms
def page_terms():
    return head("terms.html",
      "Terms of use — Floor Plan Studio",
      "The terms you use Floor Plan Studio under: it is free, it is provided as is, "
      "your drawings are yours, and it is not professional advice.") + """
<div class="wrap head">
  <span class="eyebrow"><span class="dot"></span>Terms</span>
  <h1>Terms of use</h1>
  <p class="sum">Short, because there is not much to agree to. The site is free, it
  collects nothing, and what you draw is yours.</p>
  <div class="dates"><span>Last updated: 7 September 2026</span>
    <span>Effective: 7 September 2026</span></div>
</div>

<main id="main"><div class="wrap">

<section class="col">
  <span class="ref">Section 01</span>
  <h2>Using the site</h2>
  <p>Floor Plan Studio and the guides on this site are free to use, for personal or
  commercial purposes, with no account and no licence to buy. You may use plans you draw
  with it for anything you like, including paid work.</p>
  <p>By using the site you accept these terms. If you do not accept them, do not use
  it &mdash; there is nothing to uninstall.</p>
</section>

<section class="col">
  <span class="ref">Section 02</span>
  <h2>What you draw is yours</h2>
  <p>You keep every right in the plans, drawings and files you create. Nothing is
  transmitted to this site or to anyone else, so no claim over your content is possible
  even in principle &mdash; see the <a href="privacy.html">privacy policy</a> for how
  that works.</p>
  <p>You are responsible for keeping your own copies. Work in progress lives in your
  browser&rsquo;s local storage, which you or your browser can clear at any time. If a
  plan matters to you, save it to a file.</p>
</section>

<section class="col">
  <span class="ref">Section 03</span>
  <h2>No warranty</h2>
  <p>The site is provided <b>as is</b>, without warranty of any kind. It may contain
  errors, it may be unavailable, and a browser update may break something. It is
  maintained by one person in their spare time and comes with no guarantee of
  availability, accuracy or fitness for any particular purpose.</p>
  <p>To the fullest extent the law allows, I am not liable for any loss arising from
  using the site &mdash; including furniture that does not fit, work carried out on the
  basis of a plan drawn here, or data lost from your browser&rsquo;s storage.</p>
</section>

<section class="col">
  <span class="ref">Section 04</span>
  <h2>Not professional advice</h2>
  <p>Nothing on this site is architectural, structural, electrical or safety advice. The
  furniture dimensions are generic industry standards, not any manufacturer&rsquo;s
  specification. The clearance figures are established rules of thumb for laying out a
  home, not building regulations or accessibility standards.</p>
  <p><b>Measure the actual product and the actual room before you buy or build
  anything.</b> Where work must meet a regulation, take that from the regulations where
  you live and from someone qualified to apply them.</p>
</section>

<section class="col">
  <span class="ref">Section 05</span>
  <h2>Acceptable use</h2>
  <p>Do not use the site to break the law, and do not try to break it for other people
  &mdash; no attempts to disrupt it, no automated hammering, no passing it off as your
  own service. Beyond that there is nothing to misuse: there are no accounts to abuse and
  no other users' data to reach.</p>
</section>

<section class="col">
  <span class="ref">Section 06</span>
  <h2>Advertising</h2>
  <p>This site may carry ordinary display advertising to cover its costs. Ads, if
  present, appear on the content pages and never inside the planner, never as a pop-up,
  pop-under or interstitial, and never over your drawing.</p>
  <p>Advertisers are not endorsed by me, and I have no control over what is shown or over
  the goods and services advertised. Anything you buy from an ad is between you and that
  advertiser. What advertising means for your data is set out in the
  <a href="privacy.html">privacy policy</a>.</p>
</section>

<section class="col">
  <span class="ref">Section 07</span>
  <h2>Changes and contact</h2>
  <p>These terms may change. The date at the top will say when they last did, and
  continuing to use the site after a change means the updated terms apply to you.</p>
  <p>Questions about any of this:
  <a href="mailto:tare2fo2ad@gmail.com">tare2fo2ad@gmail.com</a>.</p>
</section>

</div>
</main>
""" + foot()


if __name__ == "__main__":
    write("furniture-sizes.html",  page_furniture())
    write("room-clearances.html",  page_clearances())
    write("measure-a-room.html",   page_measure())
    write("guides.html",           page_guides())
    write("about.html",            page_about())
    write("terms.html",            page_terms())
