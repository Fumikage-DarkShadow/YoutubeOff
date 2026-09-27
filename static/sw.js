// Service worker : garde l'interface utilisable même sans le PC.
// Les vidéos hors ligne sont stockées dans IndexedDB (géré par la page).
const SHELL = "youtubeoff-shell-v1";
const SHELL_URLS = ["/", "/static/manifest.json", "/static/icon-192.png", "/static/icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(SHELL).then((c) => c.addAll(SHELL_URLS)));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== SHELL).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  const url = new URL(e.request.url);
  // Interface : réseau d'abord, cache en secours (mode hors ligne)
  if (url.pathname === "/" || url.pathname.startsWith("/static/")) {
    e.respondWith(
      fetch(e.request)
        .then((r) => {
          const clone = r.clone();
          caches.open(SHELL).then((c) => c.put(e.request, clone));
          return r;
        })
        .catch(() => caches.match(e.request))
    );
  }
  // /api et /media : réseau uniquement (le hors ligne vidéo passe par IndexedDB)
});
