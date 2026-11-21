// Vivaran's panel inside Claude, ChatGPT and other MCP Apps hosts.
//
// One page, three views, picked by `structuredContent.view` in the tool result:
//   plan     from `estimate`: the outline scene by scene, the length against the
//            length the user chose, and what the render will cost.
//   render   from `render`: live progress (it asks `video_progress` every few
//            seconds), then the finished video playing here.
//   account  from `account`: plan, credits and limits.
// Buttons never change anything by themselves: they send the user's words into
// the chat ("Render it", "Make it 8 minutes"), and the assistant acts on them.

import { App, PostMessageTransport, applyDocumentTheme, applyHostFonts, applyHostStyleVariables } from "@modelcontextprotocol/ext-apps";

type Json = Record<string, any>;

const app = new App({ name: "Vivaran", version: "1.0.0" }, {}, { autoResize: true });
const root = document.getElementById("root")!;
let poll: number | undefined;

// ---------------------------------------------------------------- helpers

function h(tag: string, attrs: Json = {}, ...children: (Node | string | null | undefined | false)[]): HTMLElement {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === undefined || v === null || v === false) continue;
    if (k.startsWith("on")) el.addEventListener(k.slice(2), v as EventListener);
    else if (k === "style") el.setAttribute("style", String(v));
    else el.setAttribute(k, String(v));
  }
  for (const c of children) if (c !== null && c !== undefined && c !== false) el.append(c instanceof Node ? c : document.createTextNode(c));
  return el;
}

const mins = (s: number) => {
  const m = Math.floor(s / 60), r = Math.round(s % 60);
  return m ? `${m}:${String(r).padStart(2, "0")}` : `${r} s`;
};
const credits = (n: number) => `${Math.round(n * 100) / 100} credit${n === 1 ? "" : "s"}`;

function say(text: string) {
  return app.sendMessage({ role: "user", content: [{ type: "text", text }] }).catch(() => undefined);
}

function show(...nodes: (Node | null)[]) {
  root.replaceChildren(...nodes.filter((n): n is Node => !!n));
}

function bar(fraction: number, tone = "") {
  const f = Math.max(0, Math.min(1, fraction));
  return h("div", { class: "bar" }, h("div", { class: `fill ${tone}`, style: `width:${(f * 100).toFixed(1)}%` }));
}

// ---------------------------------------------------------------- plan

function plan(d: Json) {
  const seconds: number = d.seconds ?? 0;
  const target: number | null = d.target_minutes ?? null;
  const outline: Json[] = d.outline ?? [];
  const longest = Math.max(1, ...outline.map((o) => o.seconds ?? 0));
  const off = target ? seconds / 60 / target - 1 : 0;
  const tone = !target ? "" : Math.abs(off) <= 0.15 ? "good" : "warn";
  const verdict = !target
    ? "No length chosen yet. Pick one below."
    : Math.abs(off) <= 0.15
      ? `On target: you asked for about ${target} min.`
      : off > 0
        ? `About ${Math.round(off * 100)}% longer than the ${target} min you asked for.`
        : `About ${Math.round(-off * 100)}% shorter than the ${target} min you asked for.`;

  const input = h("input", { type: "number", min: "1", max: String(d.account?.longest_video_minutes ?? 20), step: "0.5",
    value: String(target ?? Math.max(1, Math.round(seconds / 30) / 2)), "aria-label": "Length in minutes" }) as HTMLInputElement;

  const scale = target ? Math.max(seconds, target * 60) : seconds;
  show(
    h("header", {},
      h("div", { class: "eyebrow" }, "Video plan"),
      h("h1", {}, d.title ?? "Untitled"),
      h("div", { class: "big" }, h("strong", {}, mins(seconds)), h("span", {}, ` · ${d.steps ?? 0} steps · ${outline.length} scenes`))),
    h("section", {},
      h("div", { class: "row" }, h("span", {}, "Length"), h("span", { class: `pill ${tone}` }, verdict)),
      h("div", { class: "track" },
        bar(scale ? seconds / scale : 0, tone),
        target ? h("div", { class: "marker", style: `left:${((target * 60) / scale * 100).toFixed(1)}%`, title: `${target} min` }) : null)),
    h("ol", { class: "scenes" }, ...outline.map((o, i) =>
      h("li", {},
        h("div", { class: "row" },
          h("span", { class: "scene" }, `${i + 1}. ${o.scene}`),
          h("span", { class: "muted" }, `${o.steps} steps · ${mins(o.seconds ?? 0)}`)),
        bar((o.seconds ?? 0) / longest),
        o.opens_with ? h("p", { class: "muted quote" }, `“${o.opens_with}”`) : null))),
    d.cost !== undefined ? h("section", { class: "row cost" },
      h("span", {}, `Costs ${credits(d.cost)}${d.voice === false ? " (silent)" : ""}`),
      d.account ? h("span", { class: "muted" }, `You have ${credits(d.account.credits)} · ${d.account.tier} plan, up to ${d.account.longest_video_minutes} min`) : null) : null,
    d.problem ? h("p", { class: "warn-text" }, d.problem) : null,
    h("section", { class: "actions" },
      h("label", { class: "len" }, "Length ", input, " min"),
      h("button", { class: "ghost", onclick: () => say(`Change the script to about ${input.value} minutes: add or remove steps, then show me the plan again.`) }, "Set length"),
      h("button", { class: "primary", onclick: () => say("The plan looks right. Render it.") }, "Render")),
    h("p", { class: "fine" }, d.note ?? ""),
  );
}

// ---------------------------------------------------------------- render

const PHASES: [RegExp, string][] = [
  [/waiting/i, "Waiting for an earlier render"], [/figure/i, "Drawing figures"], [/voice (\d+)\/(\d+)/i, "Recording the voice"],
  [/listening (\d+)\/(\d+)/i, "Checking the voice"], [/render/i, "Drawing the video"], [/./, "Working"],
];

function fraction(state: string, progress: string): number {
  if (state === "done") return 1;
  const m = /(voice|listening) (\d+)\/(\d+)/i.exec(progress);
  if (m) return 0.05 + 0.6 * (Number(m[2]) / Number(m[3]));
  if (/render/i.test(progress)) return 0.8;
  return state === "queued" ? 0.02 : 0.05;
}

function rendering(d: Json, title: string) {
  const state: string = d.state ?? "queued";
  const progress: string = d.progress ?? "";
  const phase = PHASES.find(([re]) => re.test(progress))?.[1] ?? "Working";
  if (state === "done") {
    window.clearInterval(poll);
    show(
      h("header", {}, h("div", { class: "eyebrow" }, "Ready"), h("h1", {}, d.title ?? title),
        h("div", { class: "big" }, h("strong", {}, mins(d.seconds ?? 0)), h("span", {}, ` · ${d.steps ?? ""} steps · private`))),
      d.player?.video ? h("video", { controls: "", preload: "metadata", src: d.player.video, poster: d.player.poster ?? undefined }) : null,
      d.note && d.note !== "finished" ? h("p", { class: "warn-text" }, d.note) : null,
      h("section", { class: "actions" },
        h("button", { class: "ghost", onclick: () => say("Make changes to this video.") }, "Change something"),
        h("button", { class: "primary", onclick: () => app.openLink({ url: d.watch_url }) }, "Open on Vivaran")),
      h("p", { class: "fine" }, "Only you can see it. Watch it through, then make it public from its page."),
    );
    return;
  }
  if (state === "failed" || state === "unknown") {
    window.clearInterval(poll);
    show(
      h("header", {}, h("div", { class: "eyebrow danger" }, "Render failed"), h("h1", {}, d.title ?? title)),
      h("p", { class: "warn-text" }, d.error ?? "Something went wrong."),
      h("p", { class: "fine" }, "Its credits were given back."),
      h("section", { class: "actions" }, h("button", { class: "primary", onclick: () => say("The render failed. Fix the problem and try again.") }, "Ask to fix it")),
    );
    return;
  }
  show(
    h("header", {}, h("div", { class: "eyebrow" }, "Rendering"), h("h1", {}, d.title ?? title)),
    h("section", {},
      h("div", { class: "row" }, h("span", {}, phase), h("span", { class: "muted" }, progress)),
      bar(fraction(state, progress), "live"),
      h("div", { class: "row muted" }, h("span", {}, `${mins(d.elapsed_seconds ?? 0)} so far`),
        d.estimated_minutes ? h("span", {}, `about ${d.estimated_minutes} min of video`) : null)),
    h("p", { class: "fine" }, "You can keep chatting; this updates by itself."),
  );
}

function watch(job: string, first: Json) {
  const title = first.title ?? "Your video";
  rendering({ ...first, state: first.state ?? "queued" }, title);
  const tick = async () => {
    try {
      const r = await app.callServerTool({ name: "video_progress", arguments: { job } });
      const d = (r.structuredContent ?? {}) as Json;
      rendering({ estimated_minutes: first.estimated_minutes, ...d }, title);
    } catch { /* a missed poll is fine; the next one catches up */ }
  };
  window.clearInterval(poll);
  poll = window.setInterval(tick, 3000);
  tick();
}

// ---------------------------------------------------------------- account

function account(d: Json) {
  const monthly: number = d.monthly_credits_left ?? 0;
  const bonus: number = d.bonus_credits ?? 0;
  show(
    h("header", {}, h("div", { class: "eyebrow" }, `${String(d.tier ?? "free").toUpperCase()} plan`),
      h("div", { class: "big" }, h("strong", {}, String(Math.round((d.credits ?? 0) * 100) / 100)), h("span", {}, " video credits"))),
    h("section", {},
      h("div", { class: "row" }, h("span", {}, "This month"), h("span", { class: "muted" }, credits(monthly))),
      h("div", { class: "row" }, h("span", {}, "Bonus (never expire)"), h("span", { class: "muted" }, credits(bonus))),
      d.held ? h("p", { class: "warn-text" }, "Free credits are on hold for this account. Ask for them to be released.") : null,
      d.admin ? h("p", { class: "muted" }, "Admin account: renders do not use credits.") : null),
    h("section", {},
      h("div", { class: "row" }, h("span", {}, "Longest video"), h("span", { class: "muted" }, `${d.longest_video_minutes} min`)),
      h("div", { class: "row" }, h("span", {}, "Your own Gnani key"), h("span", { class: "muted" }, d.own_gnani_key ? "yes, a quarter price" : "no")),
      h("p", { class: "fine" }, d.cost ?? "")),
    h("section", { class: "actions" },
      h("button", { class: "ghost", onclick: () => app.openLink({ url: d.limits_url ?? d.more_credits }) }, "Ask for a higher limit"),
      h("button", { class: "primary", onclick: () => app.openLink({ url: d.more_credits }) }, "Get more credits")),
  );
}

// ---------------------------------------------------------------- wiring

function onResult(result: Json) {
  const d = (result.structuredContent ?? {}) as Json;
  if (result.isError) {
    const text = (result.content ?? []).map((c: Json) => c.text ?? "").join(" ");
    show(h("header", {}, h("div", { class: "eyebrow danger" }, "Vivaran")), h("p", { class: "warn-text" }, text || "That did not work."));
    return;
  }
  if (d.view === "plan") plan(d);
  else if (d.view === "render" && d.job) watch(d.job, d);
  else if (d.view === "account") account(d);
}

app.ontoolinput = () => show(h("p", { class: "muted" }, "Working…"));
app.ontoolresult = (result) => onResult(result as Json);
app.onhostcontextchanged = (ctx) => {
  if (ctx.theme) applyDocumentTheme(ctx.theme);
  if (ctx.styles?.variables) applyHostStyleVariables(ctx.styles.variables);
  if (ctx.styles?.css?.fonts) applyHostFonts(ctx.styles.css.fonts);
};
app.onteardown = async () => {
  window.clearInterval(poll);
  return {};
};

show(h("p", { class: "muted" }, "Loading…"));
app.connect(new PostMessageTransport(window.parent, window.parent)).then(() => {
  const ctx = app.getHostContext();
  if (ctx) app.onhostcontextchanged?.(ctx);
});
