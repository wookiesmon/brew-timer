// Offline support for Ebb. Same strategy as the brew timer's worker:
// the page is network-first, static assets cache-first.
// BUILD_STAMP_DEV is replaced per deploy so each deploy updates the worker.
const VERSION = "BUILD_STAMP_DEV";
const CACHE = "ebb-" + VERSION;
const SHELL = ["./", "./i18n/en.js", "./i18n/ko.js", "./manifest.json", "./icon.svg", "./icon-192.png", "./icon-512.png", "./apple-touch-icon.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith("ebb-") && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;

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
      if (res.ok) {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy));
      }
      return res;
    }))
  );
});
