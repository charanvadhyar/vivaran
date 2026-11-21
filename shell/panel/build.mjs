// Builds shell/cevg_shell/panel.html: one self-contained page (script and styles
// inline), because the host shows it in a sandbox that loads nothing else.
//   cd shell/panel && npm install && node build.mjs
import { build } from "esbuild";
import { readFileSync, writeFileSync } from "node:fs";

const out = await build({ entryPoints: ["panel.ts"], bundle: true, minify: true, format: "esm", target: "es2020", write: false });
const js = out.outputFiles[0].text.replace(/<\/script/gi, "<\\/script");
const css = readFileSync("panel.css", "utf8");
const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vivaran</title>
<style>${css}</style>
</head>
<body>
<div id="root"></div>
<script type="module">${js}</script>
</body>
</html>
`;
writeFileSync("../cevg_shell/panel.html", html);
console.log(`wrote cevg_shell/panel.html (${Math.round(html.length / 1024)} KB)`);
