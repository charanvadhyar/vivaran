# CEVG

Turns a CS or math explanation into a narrated video. Claude writes a scene
script, a Rust core draws it, and a Python shell adds Sarvam voiceover and
serves the whole thing to Claude over MCP.

## Status

Milestones 1 to 5 of 8 are done: the scene script and validator, still
frames, all seven families, and animated silent video, with captions for
checking a script by eye. Milestone 6, voice, is written from the Sarvam
documentation and tested against a stand-in server; and it runs against the real
Sarvam service. Milestone 7, the MCP server, is written and tested with an
MCP client over stdio and HTTP; it has not yet been connected to Claude
Desktop or ChatGPT. Next is hosting.

`cevg guide` prints the reference for writing scripts: what can be drawn,
how parts are named, what each action does and how to plan scenes from the
narration. It is the text handed to Claude before it writes a script, and a
test keeps it in step with the code.

## Families

Seven flat families cover the whole of CS between them, and an eighth
draws in three dimensions. All are built.

| Family | Script type | Draws | State |
| --- | --- | --- | --- |
| Sequence | `array` | arrays, stacks, queues, registers | built |
| Node-link | `diagram` | trees, graphs, neural networks, state machines, block diagrams | built |
| Table | `table` | database tables, matrices, page tables, DP tables | built |
| Math | `math` | typeset equations, revealed and rewritten line by line | built |
| Code and text | `code`, `text` | source with a current-line marker; titles and captions | built |
| Plot | `plot` | functions, loss curves, data points | built |
| Timeline | `timeline` | scheduling charts, pipeline stages, message sequences | built |
| Space (3D) | `space` | points, vectors, planes, surfaces and paths with an orbiting camera: PCA and SVD in 3D, loss surfaces, projections | built |

`pointer` and `arrow` attach to a part of any object.

## Layout of the code

| Path | What it is |
| --- | --- |
| `crates/cevg-core/src/script.rs` | The scene script: objects, scenes, steps, actions. |
| `crates/cevg-core/src/target.rs` | Targets such as `arr[3]`, `tbl[2][1]`, `net.h1->out`. |
| `crates/cevg-core/src/families/` | One module per family: its fields, state, rules, layout and painting. `mod.rs` is the only file that lists them all. |
| `crates/cevg-core/src/state.rs` | The world: every object at one moment. `World::apply` checks an action and carries it out. |
| `crates/cevg-core/src/validate.rs` | Replays a script through the world and reports problems with exact paths. |
| `crates/cevg-core/src/render.rs` | Regions, slots and the drawing context families draw with. |
| `crates/cevg-core/src/draw.rs` | The display list families record into, the blend between lists, and the rasteriser. |
| `crates/cevg-core/src/anim.rs` | Timing, the picture at any moment, parallel frames and the `ffmpeg` pipe. |
| `crates/cevg-core/src/text.rs` | Text shaping and drawing, with bundled fonts. |
| `crates/cevg-core/src/space3d.rs` | 3D: the camera, projection, solids and the `SpaceBackend` trait. |
| `crates/cevg-core/src/soft.rs` | The software 3D rasteriser (reference backend). |
| `crates/cevg-gpu` | The Vulkan 3D backend (`ash`), with its shaders. |
| `crates/cevg-cli` | The `cevg` command-line tool. |
| `shell/cevg_shell/sarvam.py` | The Sarvam text-to-speech client: one request, retries, request spacing. |
| `shell/cevg_shell/voice.py` | Voices and the cache of spoken lines. |
| `shell/cevg_shell/narrate.py` | Script to narrated video: speak, measure, render, place the audio, mux. |
| `shell/cevg_shell/server.py` | The MCP server: guide, validate, preview, render, status. |
| `examples/` | Scripts, one per subject under `subjects/`, broken scripts, rendered frames. |

Adding a family means one new module under `families/`, one variant in
`families::Body` and one in `script::ObjectKind`.

## Try it

```
cargo build --release
./target/release/cevg validate examples/subjects/ml_network.json
./target/release/cevg frame examples/subjects/ml_network.json -o ml.png
./target/release/cevg frame examples/subjects/db_join.json --step 1 -o join.png
./target/release/cevg frame examples/binary_search.json --scene first-check --step 1 --at 0.75 -o moving.png
./target/release/cevg render examples/subjects/ml_network.json -o ml.mp4
./target/release/cevg render examples/binary_search.json --speech 3,4,3,5,2.5,4,5 -o bs.mp4
./target/release/cevg render examples/subjects/ml_pca.json --captions -o pca.mp4
./target/release/cevg guide
./target/release/cevg validate examples/broken/dangling_pointer.json
cargo test --release
```

`render` needs `ffmpeg` on the PATH.

Building needs Rust 1.92 or later (`rustup update stable`); older
compilers cannot build Typst 0.15. On Windows the program is
`target\release\cevg.exe`; the commands are otherwise the same.

The first build takes several minutes because it compiles Typst.

Exit codes: 0 success, 1 the script has errors, 2 bad usage or unreadable
file. `--json` prints the full report for the Python shell and the MCP server.

`frame` draws one moment. Without `--scene` it uses the last scene; without
`--step`, the last step of that scene. Steps count from 0, matching the paths
in error messages. `--at` says how far through the step, from 0 (nothing has
moved) to 1 (the step has finished, the default).

`render` writes an H.264 MP4. `--speech` gives the narration length of every
step in seconds, in order across all scenes; this is where measured audio
lengths will go. Without it, lengths are estimated from the English text.

`--captions` (on `frame` and `render`) shows each step's narration in a band
under the picture, in English or the language named after it
(`--captions te`). The picture is laid out in the space above the band, so
nothing is covered. `render` also writes an `.srt` file beside the video.

## Voice

The Python shell in `shell/` speaks every step with Sarvam (model
`bulbul:v3`), measures each clip, renders the video to those lengths and
puts the audio under it. It needs Python 3.10 or later and nothing from pip;
`ffmpeg` and `ffprobe` must be on the PATH, and the `cevg` binary must be
built.

```
cargo build --release
cd shell
python -m unittest discover -s tests -v          # no key needed

python -m cevg_shell narrate ../examples/binary_search.json --dry-run -o bs.mp4

export SARVAM_API_KEY=your-key                    # PowerShell: $env:SARVAM_API_KEY = "your-key"
python -m cevg_shell check --lang en              # one sentence, written to check.wav
python -m cevg_shell narrate ../examples/binary_search.json -o bs.mp4
python -m cevg_shell narrate ../examples/subjects/ml_pca.json --captions -o pca.mp4
python -m cevg_shell speakers
```

The key is read only from the `SARVAM_API_KEY` environment variable. It is
never written to disk, to the cache or to any output.

`--dry-run` uses a tick and silence in place of speech, so the whole
pipeline can be tested with no key and no cost.

`--lang` picks the narration (`en`, `hi`, `te`, and the other Bulbul
languages). Every step must have that language in its `say`; the error lists
the steps that do not. `--speaker` picks the voice (default `shubh`),
`--pace` the speed (0.5 to 2.0), `--captions` burns the narration in.

Spoken lines are cached in `.cevg-cache/` in the folder you run from
(`--cache` moves it), keyed by the
text, language, voice and settings. Rendering again after changing three
sentences pays for three sentences. `ml_pca.json` is about 6,500 characters
in English; check the price per character on the Sarvam dashboard before a
long run.

How the pieces meet: the shell runs `cevg render --speech <seconds,...>
--json`, reads back where each step starts, and places each clip at that
moment on one audio track. The video is not re-encoded when the audio is
added.

What is known to be untested: everything that only the real service can
show. That is the exact error bodies, the real rate limit on your plan, how
Bulbul reads numbers and symbols, and whether a Telugu sentence with English
terms sounds right. The client follows the documentation of 1 October 2026:
`POST https://api.sarvam.ai/text-to-speech`, header `api-subscription-key`,
answer `{"audios": [base64 WAV]}`, at most 2,500 characters per request,
403 for a bad key, 429 for both rate limits (retried) and spent credits (not
retried).

The design document planned a pyo3 binding between Python and Rust. The
shell calls the `cevg` binary instead. It is simpler to build and the cost
is one process start per video. The binding can come with the MCP server if
it is still wanted.

## MCP server: Claude and ChatGPT

`shell/cevg_shell/server.py` is one MCP server with eight tools, in the
order an assistant should use them:

| Tool | What it does |
| --- | --- |
| `guide` | Returns the authoring guide. Read once before writing a script. |
| `validate` | Checks a script and returns each problem with its exact path. |
| `preview` | Draws one moment as a picture, to check the layout by eye. |
| `estimate` | Length in minutes and an outline of the scenes, without rendering. |
| `voices` | Lists the narration voices and languages, for the user to choose from. |
| `voice_sample` | Makes a short audio sample of one voice so the user can hear it. |
| `render` | Starts making the video and returns a job id at once. |
| `status` | Says how the job is going; when done, gives the link and file path. |

Rendering takes minutes, longer than an assistant waits for one tool call,
so `render` starts a job and `status` is asked until it is done. One video
renders at a time; others wait their turn.

It needs one package: `pip install "mcp>=2.3"`. Everything else in the
shell still runs without it.

The tools that only read (`guide`, `validate`, `preview`, `estimate`,
`voices`, `status`) are marked read-only, so an app can run them without
asking each time. In Claude Desktop, choose "Always allow" the first time
each tool asks, or set the whole connector to always allow in its settings.

### Claude Desktop (same computer, stdio)

Add this to `claude_desktop_config.json` (Settings, Developer, Edit Config),
with your own paths, then restart Claude Desktop:

```json
{
  "mcpServers": {
    "cevg": {
      "command": "python",
      "args": ["-m", "cevg_shell", "serve"],
      "env": {
        "PYTHONPATH": "C:\\Users\\you\\cevg\\shell",
        "SARVAM_API_KEY": "your-key"
      }
    }
  }
}
```

Videos are written to `cevg-videos` in your home folder (`--out` changes
it). Without `SARVAM_API_KEY` the server still works and makes silent
videos with captions.

### ChatGPT, and Claude on the web (HTTP)

These reach a server only over the internet, so the server runs on your
computer and a tunnel gives it a public https address.

```
cloudflared tunnel --url http://127.0.0.1:8765
```

Copy the `https://....trycloudflare.com` address it prints, then in a
second terminal:

```
cd shell
$env:SARVAM_API_KEY = "your-key"
python -m cevg_shell serve --http --public-url https://....trycloudflare.com
```

The server prints the connector address, which ends in `/<secret>/mcp`.
In ChatGPT: Settings, Security and login, turn on Developer mode; then
create an app for a remote MCP server with that address and "No
authentication". In Claude: Settings, Connectors, add a custom connector
with the same address.

The secret in the address is the only lock. Anyone who has the address can
spend your Sarvam credits, so treat it like a password. Set `--secret` or
`CEVG_SECRET` to keep the same address between runs; otherwise a new one is
made each time. A quick tunnel's address also changes each time it starts.

## Slides

`python -m cevg_shell slides script.json -o deck.pptx [--lang te]` turns a
script into a PowerPoint deck: a title slide, a divider per scene, and for
each step that works a formula two full-bleed slides: the formula as
written, and the output once the numbers have gone in (`--frames formula`,
the default; `--frames 1|2|3` takes that many exact states instead). Other
steps get their finished picture. Identical pictures are dropped, and the
narration goes in the speaker notes. `--pick "centre:4,kept:2@1"` keeps only
the named steps (finished, or after `@n` actions) for a short summary deck;
`--front deck.json` puts text slides (heading, lead, points, a callout)
before the pictures, as in `examples/decks/pca-front.json`, and `--back`
puts them after (`pca-back.json`); `--subtitle`
sets the title slide's second line; `--no-title` and `--no-dividers` drop
the framing slides. Needs
`pip install python-pptx`.

`cevg frame … --after <n>` draws the exact state of a step with its first
`n` actions complete and the rest not started, nothing half-faded; it is
what the deck uses.

## Platform

`platform/` is the website: Google sign-in, a personal connector address
per creator, a private library, and public watch pages. It runs beside the
multi-user MCP server (`python -m cevg_shell serve-platform`). See
`platform/README.md`.

`cevg render` and `cevg frame` take `--watermark <text>`, shown faintly in
the top right corner; the platform uses it on every video.

## How motion works

- A step lasts as long as its speech, plus a hold of 0.35 seconds on the
  finished picture.
- Every action starts at its `delay` (a fraction of the speech) and stretches
  to the end of the speech, easing in and out.
- Nothing is animated by hand. Families record what they draw before and
  after each action, each drawn thing under a stable name, and the two
  pictures are blended: positions, sizes and colours glide; content that is
  replaced fades out and the new content fades in after it; things that appear
  arrive in the second half of the action, once their neighbours have made
  room; lines and arrows are drawn out from their start.
- Array elements and table rows keep their identity, so a `swap` makes two
  cells trade places and an `insert` makes the others slide apart.
- A frame depends only on its own time, so frames render in parallel and any
  frame can be previewed alone. A 1080p video renders faster than it plays on
  two cores.

## Targets

| Target | Meaning |
| --- | --- |
| `arr` | the whole object |
| `arr[3]` | part 3, from 0: an array cell, a table row, a math line |
| `arr[0..3]`, `arr[0..=3]` | a range, end excluded or included |
| `tbl[2][1]` | a table cell: row 2, column 1 |
| `tbl.name`, `net.h1` | a named part: a table column, a diagram node, a plot curve or point, a timeline block, message or lane |
| `net.h1->out` | a diagram edge |

## Actions

| Action | Works on | Does |
| --- | --- | --- |
| `show`, `hide` | any whole object | objects start hidden |
| `highlight` | any part | the moving focus; clears earlier highlights on that object |
| `mark` | any part | a lasting mark: visited, sorted, done |
| `dim` | any part | fades the box, keeps the content readable |
| `reset` | any part | clears highlight, mark and dim |
| `move` | any placed object | changes its region |
| `set` | array cell, table cell, node, edge, math line, text, curve function, point label, block or message label | changes the content |
| `remove` | array cell, table row, node, edge, curve, point, block, message | takes the part away |
| `write`, `replace` | text | types it in; changes it |
| `swap`, `compare`, `insert` | array | |
| `point` | pointer | aims it at another part |
| `draw`, `retarget` | arrow | |
| `goto_line`, `mark_lines` | code | one-based line numbers |
| `add_node`, `add_edge` | diagram | |
| `add_row` | table | |
| `reveal` | math | shows lines up to the target line |
| `trace` | plot | draws a curve declared with `"visible": false` |
| `move_to` | plot | moves a point to `at: [x, y]` |
| `add_point` | plot | |
| `add_block`, `add_message` | timeline | |
| `advance` | timeline | moves the "now" cursor to a time |

## Diagram layouts

| Layout | Placement | Used for |
| --- | --- | --- |
| `layers` | columns by distance from the sources; a node may pin its `layer` | neural networks, pipelines, flowcharts |
| `tree` | children under their parent | search trees, heaps, parse trees |
| `ring` | around an ellipse | state machines, small cyclic graphs |
| `grid` | each node gives `at: [column, row]` | block diagrams |

Other diagram fields: `direction` (`right` or `down`), `shape` (`box`,
`circle`, `pill`, per diagram or per node), `directed` (default true) and
`groups` (labelled frames around sets of nodes).

## Plot

A plot has `x` and `y` axes (`label`, `min`, `max`), `curves` and `points`.
A curve is a function of `x` (`"fn": "(x - 3)^2"`) or data
(`"points": [[0, 1], [1, 0.6]]`). Functions use numbers, `x`, `pi`, `e`,
`+ - * / ^`, parentheses and `sin cos tan exp ln log log2 sqrt abs tanh
sigmoid relu floor`; `2x` and `3(x - 1)` work. A function needs `x.min` and
`x.max`. A missing y range is worked out from what is drawn, but giving it
keeps the axes still. Setting a curve to a new function morphs it.

## Timeline

A timeline has `lanes`, an optional `end` and `unit`, `blocks`
(`id, lane, start, end, label`) and `messages`
(`id, from, to, at, arrive, label`). Blocks in one lane may not overlap.
`now` or `advance` puts a cursor on the axis. Give `end` up front so the axis
does not stretch as blocks are added.

## Space (3D)

A `space` object has `axes` (ranges, `labels`, a `grid` plane), a `camera`
(`azimuth`, `elevation`, `distance`, `target`, `fov`; `z` is up) and `parts`:
`point`, `vector`, `plane` (`normal` + `size`, or `span` of two vectors),
`surface` (`fn` of `x` and `y`), `path` and `label`. Actions: `orbit`,
`look`, `trace`, `add_point`, `add_vector`, `add_plane`, `move_to`, `set`,
`project`, `rotate`, `span`, `remove`. The family computes all geometry on
the CPU (`families/space.rs`) and records it in the display list, so the
camera, coordinates and surfaces interpolate like everything else; a
backend rasterises each viewport. Two backends share one trait
(`space3d::SpaceBackend`): the software rasteriser in `cevg-core/src/soft.rs`
(a depth buffer, 2x supersampling, the reference for tests) and Vulkan in
`crates/cevg-gpu` (headless, offscreen, 4x MSAA, one shader; GLSL compiled
to SPIR-V with `glslangValidator` and committed under `shaders/`). `cevg gpu`
reports the device; `--gpu auto|vulkan|soft` on `frame` and `render` chooses
(`auto` takes the GPU when there is one). Labels are projected and drawn by
the 2D compositor, so they stay sharp and are never hidden by a surface. On
a machine without a GPU, Mesa's lavapipe (`mesa-vulkan-drivers` on Debian
and Ubuntu) runs the Vulkan backend in software; `CEVG_VK_VALIDATION=1`
turns on the Khronos validation layer when it is installed. Examples:
`examples/space_saddle.json`, `examples/subjects/ml_pca_3d.json`.

## Math

Math lines are written in Typst math syntax, not LaTeX: `x^2`, `a/b` or
`(a + b)/c` for fractions, `sqrt(x)`, `sum_(i=1)^n i`,
`integral_0^1 f(x) dif x`, `mat(1, 2; 3, 4)`, `alpha`, `bold(x)`, `hat(y)`,
and `"text"` in quotes for words. A line that does not typeset is a
validation error carrying Typst's own message. `$` and `#` are not allowed in
a line, and Typst runs with no access to files or the network.

## Script rules worth knowing

- Objects start hidden. Bring them in with `show` (or `write` for text and
  `draw` for arrows), or set `"visible": true`.
- Indexes count from 0. Code line numbers count from 1.
- Every step needs `say.en`. Other languages are optional and are translated
  from English when missing.
- Unknown fields are errors, so typos never pass silently.
- Warnings (an action on a hidden object, an object never shown, very long
  narration, too many cells to read) do not make a script invalid.
- The visible objects of a region stack top to bottom. A hidden object takes
  no room, so a region can show one thing in one scene and another in the
  next; when something is shown or hidden its neighbours glide to make room.
- A pointer sits under its target unless another part is in the way; then it
  moves above or to the side. Each pointer keeps one colour.
- Everything shrinks to fit its region; nothing is clipped.

## Fonts and licences

Noto Sans, Noto Sans Telugu, Noto Sans Devanagari and JetBrains Mono are
compiled into the library, so a frame looks the same on every machine. All
are under the SIL Open Font License; the licence texts sit beside the fonts
in `crates/cevg-core/assets/fonts`. Typst is Apache-2.0 and brings its own
math font, New Computer Modern Math (also OFL).
