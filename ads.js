/* =====================================================================
   Ad slots, and the note for people running a blocker.

   ONE place to put your publisher id. Every page that carries a slot
   loads this file, so there is nothing to keep in sync.

   As shipped this is switched OFF: nothing below contacts Google until
   BOTH enabled and consent are true, so the site still makes no
   third-party requests and privacy.html is still accurate.

   To switch ads on:
     1. Get approved for AdSense and create the ad units.
     2. Put your publisher id in ADS.client and the unit ids in ADS.slots.
     3. Put the same publisher id in /ads.txt at the SITE ROOT. On a custom
        domain that is example.com/ads.txt. On the github.io address the
        crawler looks at tarekfouad97.github.io/ads.txt, which this repo
        cannot serve - see DEPLOYING.md.
     4. Give UK/EEA visitors a consent banner BEFORE any ad script loads
        (Google's Funding Choices does this) and set ADS.consent from it.
     5. Rewrite privacy.html first. It currently states outright that this
        site carries no advertising and sets no cookies.
     6. Set ADS.enabled = true.

   Add ?adpreview=1 to any URL to see where the slots sit, and the
   blocker note, without loading anything from anyone.
   ===================================================================== */
var ADS = {
  enabled : false,
  consent : false,
  client  : "ca-pub-0000000000000000",
  slots   : {
    "in-content-1" : "0000000000",
    "in-content-2" : "0000000000",
    "footer"       : "0000000000"
  }
};

(function () {
  "use strict";
  var preview = /[?&]adpreview=1/.test(location.search);

  /* ---- the slots --------------------------------------------------- */
  var boxes = [].slice.call(document.querySelectorAll(".adslot"));
  if (boxes.length) {
    if (preview) {
      boxes.forEach(function (b) { b.hidden = false; b.classList.add("preview"); });
    } else if (ADS.enabled && ADS.consent && /^ca-pub-\d{10,}$/.test(ADS.client)) {
      var tag = document.createElement("script");
      tag.async = true;
      tag.crossOrigin = "anonymous";
      tag.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" +
                encodeURIComponent(ADS.client);
      document.head.appendChild(tag);

      boxes.forEach(function (b) {
        var id = ADS.slots[b.getAttribute("data-ad-slot")];
        if (!id || /^0+$/.test(id)) return;
        var ins = document.createElement("ins");
        ins.className = "adsbygoogle";
        ins.style.display = "block";
        ins.setAttribute("data-ad-client", ADS.client);
        ins.setAttribute("data-ad-slot", id);
        ins.setAttribute("data-ad-format", "auto");
        ins.setAttribute("data-full-width-responsive", "true");
        b.querySelector(".adbox").appendChild(ins);
        b.hidden = false;
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      });
    }
  }

  /* ---- the note for people running a blocker -----------------------
     Only ever appears when ads are actually switched on - there is no
     point asking someone to unblock ads that are not running. A card in
     the corner, never a modal, never over the drawing, and once it is
     dismissed it stays dismissed for a month.

     Detection is local: a bait element with the class names blockers
     hide. No request is made to anyone to work out whether one is
     present. ------------------------------------------------------- */
  var KEY = "fps-adnote", MONTH = 30 * 24 * 60 * 60 * 1000;
  if (!preview && !ADS.enabled) return;
  try {
    var seen = +localStorage.getItem(KEY);
    if (!preview && seen && Date.now() - seen < MONTH) return;
  } catch (e) {}

  var bait = document.createElement("div");
  bait.className = "ad-banner ads adsbox pub_300x250 text-ad doubleclick ad-placement";
  bait.style.cssText = "position:absolute;left:-9999px;top:-9999px;width:300px;height:250px";
  document.body.appendChild(bait);

  setTimeout(function () {
    var cs = getComputedStyle(bait);
    var blocked = bait.offsetHeight === 0 || bait.clientHeight === 0 ||
                  cs.display === "none" || cs.visibility === "hidden" ||
                  (ADS.enabled && ADS.consent && typeof window.adsbygoogle === "undefined");
    bait.remove();
    if (blocked || preview) show();
  }, 400);

  function show() {
    var n = document.createElement("aside");
    n.className = "adnote";
    n.setAttribute("role", "complementary");
    n.setAttribute("aria-label", "A note about ads");
    n.innerHTML =
      '<h3>Ads are what keep this free</h3>' +
      '<p>There is no paid tier here, no account and nothing held back. Two or ' +
      'three ads on these pages are the only thing paying for the tool. If you can, ' +
      'allow them on this site.</p>' +
      '<p style="margin-bottom:8px;color:var(--chalk)">Here is what you will never get from us:</p>' +
      '<ul><li>Pop-ups, pop-unders or interstitials</li>' +
      '<li>Anything that covers your drawing</li>' +
      '<li>Auto-playing video or sound</li>' +
      '<li>Ads inside the planner itself</li></ul>' +
      '<div class="row">' +
      '<button class="yes" type="button">I\'ve allowed it</button>' +
      '<button class="no"  type="button">Not now</button></div>';
    document.body.appendChild(n);
    requestAnimationFrame(function () { n.classList.add("in"); });

    n.querySelector(".yes").onclick = function () { location.reload(); };
    n.querySelector(".no").onclick = function () {
      try { localStorage.setItem(KEY, Date.now()); } catch (e) {}
      n.classList.remove("in");
      setTimeout(function () { n.remove(); }, 450);
    };
  }
})();
