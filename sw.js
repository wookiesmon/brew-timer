// Offline support: the timer must work with no signal.
// index.html is network-first (updates land immediately when online,
// cache serves when offline); static assets are cache-first.
// BUILD_STAMP_DEV is replaced per deploy, so each deploy ships a
// byte-different worker and the browser runs the update cycle.
const VERSION = "BUILD_STAMP_DEV";
const CACHE = "brew-timer-" + VERSION;
const SHELL = ["./", "./manifest.json", "./apple-touch-icon.png", "./icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith("brew-timer-") && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;
  // Ebb (cortisol/) has its own worker and cache; never cache it as the timer.
  if (new URL(req.url).pathname.includes("/cortisol/")) return;

  if (req.mode === "navigate") {
    e.respondWith(
      fetch(req)
        .then((res) => {
          // Only the app page itself becomes the offline copy; never a 404,
          // a .md doc, or another page that happens to be in scope.
          if (res.ok && new URL(req.url).pathname === new URL("./", location).pathname) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put("./", copy));
          }
          return res;
        })
        .catch(() => caches.open(CACHE).then((c) => c.match("./")))
    );
    return;
  }

  e.respondWith(
    caches.open(CACHE).then((c) => c.match(req)).then((hit) => hit || fetch(req).then((res) => {
      const copy = res.clone();
      caches.open(CACHE).then((c) => c.put(req, copy));
      return res;
    }))
  );
});
