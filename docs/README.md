# Floor Plan Studio — deploy notes

`index.html` is the whole application. One file, no build step, no dependencies,
no network calls at runtime. Everything a visitor draws stays in their own
browser — nothing is sent anywhere.

## Deploying

Any static host works. Pick one:

    # Cloudflare Pages / Netlify — drag this folder onto their dashboard, done.

    # Netlify CLI
    npx netlify-cli deploy --dir=. --prod

    # Vercel
    npx vercel --prod

    # GitHub Pages
    git init && git add . && git commit -m "floor plan studio"
    git branch -M main && git remote add origin <your repo> && git push -u origin main
    # then Settings → Pages → deploy from main

There is nothing to configure. No environment variables, no server.

## Before you switch ads on

1. **Privacy policy** — `privacy.html` is a starting draft. Read it, fill in the
   bracketed parts, and have someone check it. Ad networks require one.
2. **Cookie consent** — display ads set cookies, so EU/UK visitors need a
   consent banner *before* the ad script loads. Google's Funding Choices or
   Cookiebot both do this.
3. **Content** — a bare tool usually fails AdSense review as "low value
   content". Add real pages: standard furniture dimensions, how to measure a
   room, planning guides. Those also bring the search traffic that makes ads
   worth anything.
4. **Analytics** — otherwise you are guessing. Plausible or Umami avoid the
   cookie-banner problem entirely.

## A note on the numbers

The furniture catalogue uses generic industry-standard dimensions, not any
manufacturer's data, so there is nothing to license. Users should still measure
before buying — the app says so, and you should keep that.
