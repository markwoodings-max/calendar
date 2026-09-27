// Offline support: cache the app shell, serve it cache-first.
// Bump VERSION whenever you ship changes so buyers get the update.
const VERSION = "hh-v2";
const REMINDER_CACHE = "hh-reminder"; // shared with app.js — never deleted on update
const REMINDER_URL = new URL("./__reminder-state.json", self.registration.scope).href;
const SHELL = [
  "./", "index.html", "styles.css", "app.js", "config.js", "manifest.webmanifest",
  "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png", "icons/favicon.png",
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== VERSION && k !== REMINDER_CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(hit => hit || fetch(e.request).then(res => {
    const copy = res.clone();
    if (res.ok) caches.open(VERSION).then(c => c.put(e.request, copy));
    return res;
  })));
});

// ---------- daily reminder ----------

async function reminderState() {
  const res = await (await caches.open(REMINDER_CACHE)).match(REMINDER_URL);
  return res ? res.json() : {};
}

function localDayKey(d) {
  const p = n => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

async function maybeRemind() {
  const s = await reminderState();
  if (!s.on || !s.time || Notification.permission !== "granted") return;
  const now = new Date();
  const [hh, mm] = s.time.split(":").map(Number);
  if (now.getHours() * 60 + now.getMinutes() < hh * 60 + mm) return;
  const today = localDayKey(now);
  if (s.lastShown === today) return;
  // counts saved by the app are for the day it was last opened
  const remaining = s.date === today ? s.remaining : null;
  if (remaining === 0) return;
  const body = remaining
    ? `${remaining} habit${remaining === 1 ? "" : "s"} still to tick off today. Small steps count!`
    : "Time to tick off today's habits and log your mood.";
  await self.registration.showNotification(`${s.title || "Healthy Habits"}: evening check-in 🌿`, {
    body, icon: "icons/icon-192.png", badge: "icons/favicon.png", tag: "daily-reminder",
  });
  s.lastShown = today;
  await (await caches.open(REMINDER_CACHE)).put(REMINDER_URL,
    new Response(JSON.stringify(s), { headers: { "Content-Type": "application/json" } }));
}

// Chrome/Edge (installed app): the browser wakes us up roughly on the interval we asked for.
self.addEventListener("periodicsync", e => {
  if (e.tag === "daily-reminder") e.waitUntil(maybeRemind());
});

self.addEventListener("notificationclick", e => {
  e.notification.close();
  e.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(list => {
    const open = list.find(c => "focus" in c);
    return open ? open.focus() : self.clients.openWindow("./");
  }));
});
