# Floor Plan Studio — deploy notes

`app.html` is the whole application. `index.html` is the landing page that links
to it. Both sit at the repository root, which is what GitHub Pages serves by
default. The only file either of them loads from anywhere else is
`vendor/three.module.min.js`, which is in this repository — the site makes **no
third-party requests at all**, and `privacy.html` says so.

## Deploying

Any static host works. Pick one:

    # Cloudflare Pages / Netlify — drag this folder onto their dashboard, done.

    # Netlify CLI
    npx netlify-cli deploy --dir=. --prod

    # Vercel
    npx vercel --prod

    # GitHub Pages — push to main, that is all

There is nothing to configure. No environment variables, no server.

If you move the site to another domain, three URLs have to change with it:
the `<link rel="canonical">` in `index.html`, `privacy.html` and `app.html`, the
`Sitemap:` line in `robots.txt`, and every `<loc>` in `sitemap.xml`.

## Switching ads on

Everything is wired and switched off. Nothing contacts Google until you do all
of this. **Do it in this order** — step 4 is not optional, and step 1 is
currently the thing standing between you and approval.

1. **Content — done, for now.** This was the blocker. The site now carries
   `furniture-sizes.html` (all 116 catalogue pieces, generated from the app's own
   `CATALOG` so the two cannot disagree), `room-clearances.html`,
   `measure-a-room.html`, a `guides.html` hub, plus `about.html` and
   `terms.html`. That is a real site rather than a tool with a FAQ.

   If a reviewer still calls it thin, the next pages to write are room-by-room
   layout guides — small bedroom, galley kitchen, long thin living room — since
   they use the same figures and answer real searches. Add every new page to
   `sitemap.xml`.

2. **Apply to AdSense**, get approved, and create three ad units. The slots on
   the home page are named `in-content-1`, `in-content-2` and `footer`.

3. **Fill in the ids.** Everything lives in `ads.js` now — one file, loaded by
   every page that carries a slot. Put your publisher id in `ADS.client` and the
   three unit ids in `ADS.slots`.

   Then `ads.txt`, and read this bit carefully. **The crawler looks for it at the
   root of the host, not at the root of your project.** On the current address
   that means `https://tarekfouad97.github.io/ads.txt` — which this repository
   cannot serve, because the file it publishes lands at
   `tarekfouad97.github.io/Floor-Plan-Studio/ads.txt` and is never read. Two ways
   out, and only one of them is good:

   - **Use a custom domain** (see below). `example.com/ads.txt` is then the root,
     the file works, and the whole site moves out of a subdirectory.
   - Or create a second repository named exactly `tarekfouad97.github.io` and put
     `ads.txt` in it. This works, but every other site you ever host on that
     account shares the file.

4. **Rewrite `privacy.html` BEFORE you flip the switch.** As it stands it says
   outright that this site carries no advertising, sets no cookies and makes no
   third-party requests. All three stop being true the moment ads load. Section
   04 is the one to rewrite, and section 09 already promises the page will be
   updated first — keep that promise. Change the "last updated" date.

5. **Add a consent banner for the UK and EEA.** Display ads set cookies, so
   consent has to be collected *before* the ad script loads. Google's Funding
   Choices is the path of least resistance and is built into AdSense. Wire its
   result into `ADS.consent` — the loader already refuses to run without it.

6. **Set `ADS.enabled = true`** and deploy.

To see where the slots sit before any of this, add `?adpreview=1` to the home
page URL. That also shows the ad-blocker note, which otherwise only appears once
ads are actually running.

## Analytics

There is none, deliberately, and `privacy.html` says so. If you want it,
Plausible or Umami avoid the cookie-banner problem entirely — but they are still
a third-party request, so section 04 of the privacy policy has to change for
them too.

## A note on the numbers

The furniture catalogue uses generic industry-standard dimensions, not any
manufacturer's data, so there is nothing to license. Users should still measure
before buying — the app says so, the site says so, and you should keep that.
