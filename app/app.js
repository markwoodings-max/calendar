"use strict";

const CFG = window.HH_CONFIG;
const STORE_KEY = "healthy-habits-v1";
const MONTHS = ["January", "February", "March", "April", "May", "June", "July",
  "August", "September", "October", "November", "December"];
const DOW = ["S", "M", "T", "W", "T", "F", "S"];
const PROMPTS = [
  ["wins", "Wins I'm proud of"],
  ["blockers", "What got in the way"],
  ["learned", "What I learned about myself"],
  ["keep", "Habits to keep"],
  ["change", "Habits to change or drop"],
  ["next", "Next month I will…"],
];

// ---------- storage ----------

function uid() { return Math.random().toString(36).slice(2, 10); }

function freshState() {
  return {
    version: 1,
    habits: CFG.defaultHabits.map(name => ({ id: uid(), name })),
    days: {},        // "YYYY-MM-DD" -> { done: [habitId], mood, water, sleep, note }
    months: {},      // "YYYY-MM"    -> { intention, rating, word, wins, blockers, ... }
    settings: { weekStart: CFG.weekStart, waterGoal: CFG.waterGoal },
  };
}

function load() {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (raw) return Object.assign(freshState(), JSON.parse(raw));
  } catch (e) { /* fall through to a fresh state */ }
  return freshState();
}

let state = load();
function save() {
  try { localStorage.setItem(STORE_KEY, JSON.stringify(state)); }
  catch (e) { toast("Couldn't save — storage is full or blocked"); }
}

// ---------- dates (always local time, never UTC) ----------

const pad = n => String(n).padStart(2, "0");
const dayKey = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const monthKey = (y, m) => `${y}-${pad(m + 1)}`;
const daysIn = (y, m) => new Date(y, m + 1, 0).getDate();
const addDays = (d, n) => new Date(d.getFullYear(), d.getMonth(), d.getDate() + n);
const today = () => { const t = new Date(); return new Date(t.getFullYear(), t.getMonth(), t.getDate()); };
const sameDay = (a, b) => dayKey(a) === dayKey(b);

function dayData(key, create) {
  let d = state.days[key];
  if (!d && create) d = state.days[key] = { done: [] };
  return d || { done: [] };
}
function moodColor(i) { return (CFG.moods[i] || {}).color || "transparent"; }
function monthData(key) { return state.months[key] || (state.months[key] = {}); }

function completion(key) {
  const n = state.habits.length;
  if (!n) return 0;
  const ids = new Set(state.habits.map(h => h.id));
  return dayData(key).done.filter(id => ids.has(id)).length / n;
}

function streak(habitId) {
  let d = today();
  if (!dayData(dayKey(d)).done.includes(habitId)) d = addDays(d, -1);
  let n = 0;
  while (dayData(dayKey(d)).done.includes(habitId)) { n++; d = addDays(d, -1); }
  return n;
}

// ---------- tiny DOM helper (no innerHTML with user data) ----------

function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (k === "style" && typeof v === "object") Object.assign(el.style, v);
    else if (k === "value") el.value = v;
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat()) {
    if (kid == null || kid === false) continue;
    el.append(kid.nodeType ? kid : document.createTextNode(kid));
  }
  return el;
}
const svg = (tag, attrs) => {
  const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  return el;
};

let toastTimer;
function toast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), 2000);
}

// ---------- view state & routing ----------

const ui = { tab: "today", date: today(), year: today().getFullYear(), month: today().getMonth() };

function render() {
  const view = document.getElementById("view");
  view.replaceChildren(VIEWS[ui.tab]());
  drops();
  document.querySelectorAll(".tabbar button").forEach(b =>
    b.classList.toggle("active", b.dataset.tab === ui.tab));
}

function go(tab) { ui.tab = tab; render(); window.scrollTo(0, 0); }

function pager(label, onPrev, onNext, extra) {
  return h("div", { class: "pager" },
    h("button", { class: "arrow", "aria-label": "Previous", onclick: onPrev }, "‹"),
    h("div", { style: { textAlign: "center", flex: 1 } }, label, extra),
    h("button", { class: "arrow", "aria-label": "Next", onclick: onNext }, "›"));
}

function counter(value, onChange, step = 1, max = 99) {
  const out = h("output", {}, String(value ?? 0));
  const set = v => { v = Math.max(0, Math.min(max, v)); out.textContent = String(v); onChange(v); };
  return h("div", { class: "counter" },
    h("button", { "aria-label": "Decrease", onclick: () => set(Number(out.textContent) - step) }, "−"),
    out,
    h("button", { "aria-label": "Increase", onclick: () => set(Number(out.textContent) + step) }, "+"));
}

// ---------- Today ----------

function viewToday() {
  const d = ui.date;
  const key = dayKey(d);
  const data = dayData(key);
  const isToday = sameDay(d, today());
  const pct = completion(key);
  const done = Math.round(pct * state.habits.length);

  const R = 32, C = 2 * Math.PI * R;
  const ring = svg("svg", { class: "ring", viewBox: "0 0 76 76" });
  ring.append(
    svg("circle", { class: "track", cx: 38, cy: 38, r: R }),
    svg("circle", { class: "bar", cx: 38, cy: 38, r: R, "stroke-dasharray": C,
      "stroke-dashoffset": C * (1 - pct), transform: "rotate(-90 38 38)" }));
  const label = svg("text", { x: 38, y: 44, "text-anchor": "middle" });
  label.textContent = `${Math.round(pct * 100)}%`;
  ring.append(label);

  const title = isToday ? "Today" : d.toLocaleDateString(undefined, { weekday: "long" });
  const sub = d.toLocaleDateString(undefined, { day: "numeric", month: "long", year: "numeric" });

  const toggle = id => {
    const day = dayData(key, true);
    const i = day.done.indexOf(id);
    if (i >= 0) day.done.splice(i, 1); else day.done.push(id);
    save(); render();
    if (i < 0 && completion(key) === 1) toast("Every habit done — brilliant! 🌿");
  };

  return h("section", {},
    pager(h("div", {}, h("h2", {}, title), h("p", { class: "sub", style: { margin: 0 } }, sub)),
      () => { ui.date = addDays(d, -1); render(); },
      () => { ui.date = addDays(d, 1); render(); },
      !isToday && h("button", { class: "pill", style: { marginTop: "6px" },
        onclick: () => { ui.date = today(); render(); } }, "Back to today")),
    h("div", { class: "card progress", style: { marginTop: "16px" } }, ring,
      h("div", {},
        h("div", { style: { fontWeight: 700, color: "var(--primary)" } },
          `${done} of ${state.habits.length} habits`),
        h("div", { class: "muted small" },
          pct === 1 ? "Perfect day. Enjoy it." : pct >= .5 ? "More than halfway there." :
            "Small steps count. Never miss twice."))),
    h("div", { class: "card" }, h("h3", {}, "Habits"),
      state.habits.length === 0
        ? h("p", { class: "muted" }, "No habits yet — add some in the Habits tab.")
        : h("div", { class: "habits" }, state.habits.map(hb => {
          const on = data.done.includes(hb.id);
          const s = streak(hb.id);
          return h("button", { class: "habit", "aria-pressed": String(on), onclick: () => toggle(hb.id) },
            h("span", { class: "check" }, "✓"),
            h("span", { class: "name" }, hb.name),
            s > 1 && h("span", { class: "streak" }, `🔥 ${s}`));
        }))),
    h("div", { class: "card" }, h("h3", {}, "Mood"),
      h("div", { class: "moods" }, CFG.moods.map((m, i) =>
        h("button", { class: "mood", "aria-pressed": String(data.mood === i),
          onclick: () => { const day = dayData(key, true); day.mood = day.mood === i ? undefined : i; save(); render(); } },
          h("span", { class: "dot", style: { background: m.color } }), m.label)))),
    h("div", { class: "card" },
      h("div", { class: "row spread" },
        h("h3", { style: { margin: 0 } }, "Water (glasses)"),
        counter(data.water, v => { dayData(key, true).water = v; save(); drops(); }, 1, 30)),
      h("div", { class: "drops", id: "drops" })),
    h("div", { class: "card row spread" },
      h("h3", { style: { margin: 0 } }, "Sleep (hours)"),
      counter(data.sleep, v => { dayData(key, true).sleep = v; save(); }, 0.5, 24)),
    h("div", { class: "card" }, h("h3", {}, "Note"),
      h("textarea", { rows: 3, placeholder: "One thing I'm grateful for today…", value: data.note || "",
        oninput: e => { dayData(key, true).note = e.target.value; save(); } })),
  );
}

function drops() {
  const el = document.getElementById("drops");
  if (!el) return;
  const n = dayData(dayKey(ui.date)).water || 0;
  const goal = state.settings.waterGoal;
  el.replaceChildren(...Array.from({ length: Math.max(goal, n) }, (_, i) =>
    h("span", { class: "drop" + (i < n ? " on" : "") })));
}

// ---------- Month ----------

function viewMonth() {
  const { year: y, month: m } = ui;
  const mk = monthKey(y, m);
  const first = new Date(y, m, 1).getDay();
  const offset = state.settings.weekStart === "monday" ? (first + 6) % 7 : first;
  const dows = state.settings.weekStart === "monday" ? [...DOW.slice(1), DOW[0]] : DOW;
  const n = daysIn(y, m);
  const t = today();

  const cells = [];
  for (let i = 0; i < offset; i++) cells.push(h("div", { class: "day empty" }));
  for (let day = 1; day <= n; day++) {
    const d = new Date(y, m, day);
    const key = dayKey(d);
    const pct = completion(key);
    const mood = dayData(key).mood;
    cells.push(h("button", {
      class: "day" + (pct === 1 ? " full" : "") + (sameDay(d, t) ? " today" : ""),
      "aria-label": `${MONTHS[m]} ${day}, ${Math.round(pct * 100)}% of habits`,
      onclick: () => { ui.date = d; go("today"); },
    },
      h("span", { class: "fill", style: { height: `${pct * 100}%` } }),
      h("span", { class: "num" }, String(day)),
      mood != null && h("span", { class: "md", style: { background: moodColor(mood) } })));
  }

  const move = delta => {
    const d = new Date(y, m + delta, 1);
    ui.year = d.getFullYear(); ui.month = d.getMonth(); render();
  };

  const days = Array.from({ length: n }, (_, i) => i + 1);
  const grid = h("table", { class: "grid" },
    h("thead", {}, h("tr", {}, h("th", { class: "hname" }), days.map(d => h("th", {}, String(d))), h("th", {}, "Σ"))),
    h("tbody", {}, state.habits.map(hb => {
      let total = 0;
      return h("tr", {},
        h("th", { class: "hname", title: hb.name }, hb.name),
        days.map(d => {
          const on = dayData(dayKey(new Date(y, m, d))).done.includes(hb.id);
          if (on) total++;
          return h("td", {}, h("span", { class: on ? "on" : "" }));
        }),
        h("td", { class: "tot" }, String(total)));
    })));

  return h("section", {},
    pager(h("h2", {}, `${MONTHS[m]} ${y}`), () => move(-1), () => move(1)),
    h("p", { class: "sub", style: { textAlign: "center" } }, "Tap a day to open it"),
    h("div", { class: "card" }, h("h3", {}, "This month I intend to…"),
      h("input", { type: "text", placeholder: "e.g. feel rested and strong", value: monthData(mk).intention || "",
        oninput: e => { monthData(mk).intention = e.target.value; save(); } })),
    h("div", { class: "card" },
      h("div", { class: "cal" }, dows.map(x => h("div", { class: "dow" }, x)), cells)),
    h("div", { class: "card" }, h("h3", {}, "Habit tracker"),
      state.habits.length ? h("div", { class: "grid-wrap" }, grid) : h("p", { class: "muted" }, "No habits yet.")),
  );
}

// ---------- Year ----------

function viewYear() {
  const y = ui.year;
  const cells = [h("div", {})];
  MONTHS.forEach(mn => cells.push(h("div", { class: "mh" }, mn.slice(0, 1))));
  for (let d = 1; d <= 31; d++) {
    cells.push(h("div", { class: "lab" }, String(d)));
    for (let m = 0; m < 12; m++) {
      if (d > daysIn(y, m)) { cells.push(h("div", { class: "px none" })); continue; }
      const mood = dayData(dayKey(new Date(y, m, d))).mood;
      cells.push(h("div", { class: "px", title: `${d} ${MONTHS[m]}`,
        style: mood != null ? { background: moodColor(mood), borderColor: "transparent" } : null }));
    }
  }

  // yearly stats
  let checks = 0, perfect = 0, tracked = 0, pctSum = 0;
  for (const [k, v] of Object.entries(state.days)) {
    if (!k.startsWith(String(y))) continue;
    checks += v.done.length;
    if (v.done.length) { tracked++; pctSum += completion(k); }
    if (completion(k) === 1) perfect++;
  }
  const best = Math.max(0, ...state.habits.map(hb => bestStreak(hb.id, y)));

  return h("section", {},
    pager(h("h2", {}, String(y)), () => { ui.year--; render(); }, () => { ui.year++; render(); }),
    h("p", { class: "sub", style: { textAlign: "center" } }, "Your year in pixels"),
    h("div", { class: "stats card" },
      h("div", { class: "stat" }, h("b", {}, String(checks)), h("span", {}, "habits done")),
      h("div", { class: "stat" }, h("b", {}, String(perfect)), h("span", {}, "perfect days")),
      h("div", { class: "stat" }, h("b", {}, String(best)), h("span", {}, "best streak"))),
    tracked > 0 && h("p", { class: "muted small", style: { textAlign: "center", marginTop: "-4px" } },
      `Average ${Math.round((pctSum / tracked) * 100)}% on the ${tracked} days you tracked`),
    h("div", { class: "card" }, h("div", { class: "pixels" }, cells),
      h("div", { class: "legend" }, CFG.moods.map(m => h("span", {}, h("i", { style: { background: m.color } }), m.label)))),
  );
}

function bestStreak(id, y) {
  let best = 0, run = 0;
  for (let d = new Date(y, 0, 1); d.getFullYear() === y; d = addDays(d, 1)) {
    if (dayData(dayKey(d)).done.includes(id)) best = Math.max(best, ++run); else run = 0;
  }
  return best;
}

// ---------- Reflect ----------

function viewReflect() {
  const { year: y, month: m } = ui;
  const mk = monthKey(y, m);
  const md = monthData(mk);
  let sum = 0, count = 0;
  for (let d = 1; d <= daysIn(y, m); d++) {
    const date = new Date(y, m, d);
    if (date > today()) break;
    sum += completion(dayKey(date)); count++;
  }
  const move = delta => {
    const d = new Date(y, m + delta, 1);
    ui.year = d.getFullYear(); ui.month = d.getMonth(); render();
  };

  return h("section", {},
    pager(h("h2", {}, `${MONTHS[m]}`), () => move(-1), () => move(1)),
    h("p", { class: "sub", style: { textAlign: "center" } }, "Look back, celebrate, adjust"),
    h("div", { class: "stats card", style: { gridTemplateColumns: "1fr 1fr" } },
      h("div", { class: "stat" }, h("b", {}, count ? `${Math.round(sum / count * 100)}%` : "—"), h("span", {}, "habit completion")),
      h("div", { class: "stat" },
        h("input", { type: "text", placeholder: "One word…", "aria-label": "One word for this month",
          style: { font: "400 22px var(--serif)", border: 0, background: "transparent", padding: 0, color: "var(--primary)" },
          value: md.word || "", oninput: e => { monthData(mk).word = e.target.value; save(); } }),
        h("span", {}, "one word for this month"))),
    h("div", { class: "card" }, h("h3", {}, "Rate this month"),
      h("div", { class: "rating" }, Array.from({ length: 10 }, (_, i) =>
        h("button", { "aria-pressed": String(md.rating === i + 1),
          onclick: () => { monthData(mk).rating = md.rating === i + 1 ? undefined : i + 1; save(); render(); } },
          String(i + 1))))),
    h("div", { class: "card" }, PROMPTS.map(([k, label]) =>
      h("div", { class: "prompt" }, h("label", { for: `p-${k}` }, label),
        h("textarea", { id: `p-${k}`, rows: 3, value: md[k] || "",
          oninput: e => { monthData(mk)[k] = e.target.value; save(); } })))),
  );
}

// ---------- Settings ----------

function viewSettings() {
  const list = h("div", {}, state.habits.map((hb, i) =>
    h("div", { class: "edit-row" },
      h("input", { type: "text", value: hb.name, "aria-label": `Habit ${i + 1}`, maxlength: 60,
        oninput: e => { hb.name = e.target.value; save(); } }),
      h("button", { class: "icon-btn", "aria-label": "Move up", disabled: i === 0,
        onclick: () => { [state.habits[i - 1], state.habits[i]] = [state.habits[i], state.habits[i - 1]]; save(); render(); } }, "↑"),
      h("button", { class: "icon-btn", "aria-label": "Delete",
        onclick: () => { if (confirm(`Remove "${hb.name}"? Its history stays in your backup.`)) { state.habits.splice(i, 1); save(); render(); } } }, "✕"))));

  const newInput = h("input", { type: "text", placeholder: "Add a habit…", maxlength: 60 });
  const add = () => {
    const name = newInput.value.trim();
    if (!name) return;
    state.habits.push({ id: uid(), name }); save(); render();
    toast("Habit added");
  };
  newInput.addEventListener("keydown", e => { if (e.key === "Enter") add(); });

  return h("section", {},
    h("h2", {}, "My Habits"),
    h("p", { class: "sub" }, "Small and specific beats big and vague"),
    h("div", { class: "card" }, list,
      h("div", { class: "edit-row", style: { marginTop: "12px" } }, newInput,
        h("button", { class: "btn", onclick: add }, "Add"))),
    h("div", { class: "card" }, h("h3", {}, "Preferences"),
      h("div", { class: "row spread", style: { marginBottom: "12px" } }, h("span", {}, "Week starts on"),
        h("select", { onchange: e => { state.settings.weekStart = e.target.value; save(); } },
          ["sunday", "monday"].map(v => h("option", { value: v, selected: state.settings.weekStart === v },
            v[0].toUpperCase() + v.slice(1))))),
      h("div", { class: "row spread" }, h("span", {}, "Daily water goal"),
        counter(state.settings.waterGoal, v => { state.settings.waterGoal = v || 1; save(); }, 1, 20))),
    h("div", { class: "card" }, h("h3", {}, "Your data"),
      h("p", { class: "muted small", style: { marginTop: 0 } },
        "Everything stays private on this device. Back up regularly, or to move to a new phone."),
      h("div", { class: "btns" },
        h("button", { class: "btn ghost", onclick: exportData }, "Export backup"),
        h("button", { class: "btn ghost", onclick: importData }, "Restore backup"),
        h("button", { class: "btn danger", onclick: resetData }, "Reset"))),
    h("p", { class: "footer" }, `${CFG.title} · © ${CFG.author}`, CFG.website ? ` · ${CFG.website}` : "",
      h("br"), "Not medical advice. For personal use only."),
  );
}

function exportData() {
  const blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
  const a = h("a", { href: URL.createObjectURL(blob), download: `healthy-habits-backup-${dayKey(today())}.json` });
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}

function importData() {
  const input = h("input", { type: "file", accept: "application/json,.json" });
  input.addEventListener("change", async () => {
    try {
      const data = JSON.parse(await input.files[0].text());
      if (!Array.isArray(data.habits) || typeof data.days !== "object") throw new Error("bad file");
      state = Object.assign(freshState(), data);
      save(); render(); toast("Backup restored");
    } catch (e) { toast("That doesn't look like a Healthy Habits backup"); }
  });
  input.click();
}

function resetData() {
  if (!confirm("Erase all habits, history and reflections on this device?")) return;
  state = freshState(); save(); render(); toast("Fresh start");
}

// ---------- boot ----------

const VIEWS = { today: viewToday, month: viewMonth, year: viewYear, reflect: viewReflect, settings: viewSettings };

document.getElementById("title").textContent = CFG.title;
document.title = CFG.title;
document.querySelectorAll(".tabbar button").forEach(b => b.addEventListener("click", () => {
  if (b.dataset.tab === "month" || b.dataset.tab === "reflect") {
    ui.year = ui.date.getFullYear(); ui.month = ui.date.getMonth();
  }
  go(b.dataset.tab);
}));
render();

// roll over to the new day if the app is left open past midnight
let lastDay = dayKey(today());
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible" && dayKey(today()) !== lastDay) {
    lastDay = dayKey(today()); ui.date = today(); render();
  }
});

if ("serviceWorker" in navigator && location.protocol.startsWith("http")) {
  navigator.serviceWorker.register("sw.js").catch(() => {});
}
