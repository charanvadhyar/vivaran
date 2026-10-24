# Writing a CEVG scene script

A scene script is one JSON document. It declares the objects that can appear,
then a list of scenes, each a list of steps. A step is one sentence of
narration plus the actions that play while it is spoken. You never give
coordinates, sizes or timings in seconds: you choose a region for each object
and the renderer lays out, animates and times everything.

Work in this order: write the narration, plan the screen for each scene,
declare the objects, attach actions to steps, validate, preview, fix.

## Skeleton

```json
{
  "version": 1,
  "title": "Binary search",
  "canvas": { "width": 1920, "height": 1080, "fps": 30, "theme": "dark" },
  "objects": [
    { "id": "arr", "type": "array", "region": "center", "values": [2, 5, 8, 12] }
  ],
  "scenes": [
    { "id": "setup",
      "steps": [
        { "say": { "en": "We search this sorted array for 8." },
          "do": [ { "action": "show", "target": "arr" } ] }
      ] }
  ]
}
```

- `canvas` is optional; the defaults are shown. `theme` is `dark` or `light`.
- Object ids: lowercase letters, digits and `_`, starting with a letter.
- Scene ids may also contain `-`.
- `say.en` is required on every step. Add `hi`, `te` or other languages
  beside it to narrate in them: `"say": { "en": "...", "hi": "...", "te": "..." }`.
- `do` may be empty or left out: a step can be narration only.
- Unknown fields are errors.

## Planning scenes from the narration

1. One step is one sentence, ideally 8 to 20 words. A long sentence makes
   slow motion, because actions stretch to fill the sentence.
2. Give each sentence one main thing to look at. If a sentence introduces
   two ideas, split it into two steps.
3. Say what the picture shows. Narration that mentions a value, a node or a
   line should highlight, reveal or move that same thing in the same step.
4. Plan the screen per scene. There are five regions:

   ```
   +---------------- title ----------------+
   |                                       |
   |   left          |        right        |      center = left + right
   |                                       |
   +---------------- bottom ---------------+
   ```

   Use `center` alone, or `left` and `right` together. Do not put visible
   objects in `center` and in `left`/`right` at the same time: they overlap.
5. Only visible objects take room. Visible objects that share a region stack
   top to bottom and share its height, so two is comfortable and three is
   crowded. To reuse a region in the next scene, `hide` the old object in the
   same step that shows the new one.
6. Objects start hidden. Nothing appears until a `show` (or `write` for
   text, `draw` for an arrow), unless the object sets `"visible": true`.
7. `title` holds one short heading. `bottom` holds one line: a takeaway, a
   formula, a running result.

## The teaching standard: the student must be able to redo it

A video is not finished when it shows the right answer. It is finished when
a student who watches it could reproduce the whole solution alone, in an
exam, on different numbers. Write every script to that standard:

1. **Name every symbol the first time it appears.** If a formula has n, a
   bar, a tilde, a subscript or a Greek letter, a sentence says what it
   stands for. Never show a formula and move on.
2. **Show where every number comes from.** Put the arithmetic on screen, not
   only the result: `(2 + 4 + 5 + 5) / 4 = 16 / 4 = 4`, not `mean = 4`. If a
   table column is computed, compute at least the first row out loud.
3. **Say why each step is done**, in one sentence, before doing it: what
   would go wrong without it, or what question it answers.
4. **State every choice and convention**: dividing by n − 1 or n, which root
   to take, how results are ordered, when a vector is normalised, what is
   rounded and to how many places. These are where exam marks are lost.
5. **Do one thing per step.** A step that introduces a formula does not also
   substitute numbers into it. Substitution is the next step, the result
   the one after.
6. **Include a check** the student can use to catch their own mistakes: a
   sum that must match, a product that must be zero, a value that must lie
   in a range.
7. **Number the stages and keep the number on screen** (the title is a good
   place: "Step 2 of 6: covariance matrix"). Open with the list of stages
   and close by walking through it again.
8. **Keep earlier results visible while they are being used.** If step 4
   needs the matrix from step 2, leave the matrix on screen.

Expect such a video to be long. A worked example with six stages is 40 to
60 steps and four to six minutes. That is the right length; do not compress
it.

## Length: the user chooses it

The user decides how long the video is, in minutes. Ask if they have not
said. Before writing the script, show them an outline of the scenes and
roughly how long each takes, and let them change it.

- Plan on about 7 steps for each minute. A spoken step is 6 to 12 seconds.
- One minute explains one idea with one small example. Three minutes works
  one example through. Six to nine minutes is a full exam-level derivation
  with every value explained.
- A short video covers less; it does not skip reasoning. If the length the
  user chose cannot hold the topic to the teaching standard, say so and
  offer a narrower topic or a longer video.
- After writing, check the length (the `estimate` tool, or `cevg render`
  without audio) and add or remove steps until it is close.

## Writing narration that will be spoken

The `say` text is read aloud by a text-to-speech voice and is also the
caption. Write it for the ear.

- One or two sentences per step, in plain spoken language. A sentence the
  voice can say in one breath is easier to follow than a long one.
- Write every language yourself. Do not translate word for word; say what a
  good teacher would say in that language.
- Hindi and Telugu narration is code-mixed, the way lectures are given in
  Indian colleges. Only the glue of the sentence is in the regional
  language: conjunctions and connectors (కాబట్టి, ఎందుకంటే, అంటే, కానీ;
  इसलिए, क्योंकि, यानी, लेकिन), pronouns, case endings and the light verb
  that carries the tense (చేస్తాం, అవుతుంది; करते हैं, होता है). Every word
  that carries meaning stays in English, in Latin letters: technical terms,
  and also ordinary nouns, verbs, adjectives and number words. Say
  "root 2 తో divide చేస్తాం", never "root 2 తో భాగిస్తాం"; "add करने पर",
  never "जोड़ने पर"; "zero", "sum", "equal", "subtract", "multiply".
  Write the glue words in the native script.
- Spell out what the voice cannot read. Write "x bar" or "the mean of x",
  not "x̄"; "lambda", not "λ"; "A transpose", not "A^T"; "two by two
  matrix", not "2×2 matrix"; "minus 2.12", not "−2.12"; "is less than",
  not "<". The formula itself belongs on screen in a `math` object.
- Name a cell or an element in words: "the element at index 3", not
  "arr[3]".
- Numbers are fine as digits. Write a fraction as "3 by 4" or "three
  fourths", not "3/4".
- All languages of a step should say the same thing in about the same
  length, because the same actions play under each.

## Timing

- A step lasts as long as its narration, then holds for a moment.
- Every action starts at its `delay` and runs to the end of the sentence.
  `delay` is a fraction of the sentence from 0 to 1 and defaults to 0.
- Use `delay` to order things inside a step: `0` for what the sentence opens
  with, `0.5` for what it ends on. Things that appear show up in the second
  half of their own action; things that are replaced fade out, then in.

## Targets: naming an object or a part of it

| Target | Meaning |
| --- | --- |
| `arr` | the whole object |
| `arr[3]` | part 3, counted from 0: an array cell, a table row, a math line |
| `arr[0..3]` | parts 0, 1, 2 (end excluded) |
| `arr[0..=3]` | parts 0 to 3 (end included) |
| `tbl[2][1]` | table cell: row 2, column 1 |
| `tbl.name` | a named part: table column, diagram node, plot curve or point, timeline block, message or lane, space part |
| `net.a->b` | the diagram edge from node `a` to node `b` |

## Actions for every object

| Action | Fields | What it does |
| --- | --- | --- |
| `show` | `target` (whole object) | brings the object in |
| `hide` | `target` (whole object) | takes it away and frees its room |
| `highlight` | `target` | the moving focus: lighting a part clears the parts of that object lit before |
| `mark` | `target` | a lasting mark for "visited", "sorted", "done"; stays until `reset` |
| `dim` | `target` | fades it back; stays until `reset` |
| `reset` | `target` | clears highlight, mark and dim |
| `move` | `target`, `region` | moves a whole object to another region |
| `set` | `target`, `value` | changes the content of a part (see each family) |
| `remove` | `target` | takes a part away (see each family) |

Use `highlight` for "look here now" and `mark` for "this stays true".

## Families

### text

Titles, captions, takeaways.

```json
{ "id": "note", "type": "text", "region": "bottom", "text": "Found in 2 checks" }
```

Actions: `write` (shows it), `replace` with `text`, `set` with `value`.

### array (sequence)

A row of indexed cells: arrays, stacks, queues, registers.

```json
{ "id": "arr", "type": "array", "region": "center", "values": [2, 5, 8, "x"] }
```

Parts: `arr[i]`, ranges. Up to about 16 cells stay readable.

| Action | Fields |
| --- | --- |
| `swap` | `a`, `b` (two cells; they trade places) |
| `compare` | `a`, `b` (lights both) |
| `set` | `target` (a cell), `value` |
| `insert` | `target` (the array), `index`, `value` |
| `remove` | `target` (a cell) |

### pointer and arrow

Marks that attach to a part of another object. They take no region.

```json
{ "id": "lo", "type": "pointer", "label": "lo", "target": "arr[0]" }
{ "id": "link", "type": "arrow", "from": "students[1]", "to": "depts[1]", "label": "20 = 20" }
```

Actions: `point` with `target` (the pointer) and `to`; `draw` (shows an
arrow); `retarget` with `from` and/or `to`. A part cannot be removed while a
pointer or arrow is attached to it: move the pointer first.

### code

Source lines with a current-line marker.

```json
{ "id": "src", "type": "code", "region": "left", "language": "python",
  "lines": ["lo, hi = 0, n - 1", "while lo <= hi:", "    mid = (lo + hi) // 2"] }
```

Actions: `goto_line` with `line`; `mark_lines` with `from` and `to`. Line
numbers count from 1. Keep to about 12 lines.

### diagram (node-link)

Trees, graphs, neural networks, state machines, block diagrams, pipelines.

```json
{ "id": "net", "type": "diagram", "region": "left", "layout": "layers", "shape": "circle",
  "nodes": [ { "id": "x1", "label": "x₁" }, { "id": "h1" }, { "id": "y", "label": "ŷ" } ],
  "edges": [ { "from": "x1", "to": "h1", "label": "w" }, { "from": "h1", "to": "y" } ],
  "groups": [ { "label": "hidden", "nodes": ["h1"] } ] }
```

| Field | Values |
| --- | --- |
| `layout` | `layers` (default): columns by distance from the sources, for networks, pipelines, flowcharts. `tree`: children under parents. `ring`: around an ellipse, for state machines and cyclic graphs. `grid`: every node gives `"at": [column, row]`, for block diagrams. |
| `direction` | `right` or `down`. Default: `right` for layers, `down` for trees. |
| `shape` | `box` (default), `circle`, `pill`; a node may set its own. |
| `directed` | `true` (default) draws arrowheads. |
| node | `id`, optional `label` (defaults to the id), `shape`, `layer` (pins it, layers only), `at` (grid only) |
| edge | `from`, `to`, optional `label` |
| `groups` | labelled frames around sets of nodes |

Node ids use letters, digits and `_`. Parts: `net.h1`, `net.h1->y`.

| Action | Fields |
| --- | --- |
| `set` | `target` (a node or edge), `value` (its new label) |
| `add_node` | `target` (the diagram), `id`, optional `label`, `shape`, `layer`, `at` |
| `add_edge` | `target` (the diagram), `from`, `to`, optional `label` |
| `remove` | `target` (a node, with its edges, or an edge) |

Up to about 24 nodes stay readable.

### table

Database tables, matrices, page tables, DP tables.

```json
{ "id": "emp", "type": "table", "region": "left",
  "columns": ["id", "name"], "rows": [[1, "Asha"], [2, "Ravi"]] }
```

Leave `columns` out for a plain grid. Parts: `emp[1]` a row, `emp[0..2]`
rows, `emp[1][0]` a cell, `emp.name` a column by its header, `emp.c1` a
column by position (for grids without headers, or headers such as "x − 4"
that are not plain names). A cell may start as `""` and be filled in later
with `set`, which is how a worked calculation grows column by column.

| Action | Fields |
| --- | --- |
| `set` | `target` (a cell), `value` |
| `add_row` | `target` (the table), `values`, optional `index` |
| `remove` | `target` (a row) |

Up to about 10 rows stay readable.

### math

Typeset equations, shown line by line. Lines are written in Typst math
syntax, not LaTeX.

```json
{ "id": "eq", "type": "math", "region": "right",
  "lines": ["a x^2 + b x + c = 0", "x = (-b plus.minus sqrt(b^2 - 4 a c)) / (2 a)"] }
```

Only the first line is visible at first; set `"shown": n` to start with more.
Parts: `eq[i]`. Actions: `reveal` with `target` a line (shows lines up to
it); `set` with `target` a line and `value` the new line.

Typst math in brief:

| Write | For |
| --- | --- |
| `x^2`, `x_i`, `x_(i+1)`, `e^(-z)` | powers and subscripts; group with parentheses |
| `a / b`, `(a + b) / c` | fractions |
| `sqrt(x)`, `root(3, x)` | roots |
| `sum_(i=1)^n x_i`, `product_i`, `integral_0^1 f(x) dif x` | sums, products, integrals |
| `alpha beta gamma lambda mu sigma eta theta`, `Sigma Lambda` | Greek letters by name |
| `bold(x)`, `hat(y)`, `tilde(x)`, `overline(x)`, `vec(1, 2)` | bold, accents, column vector |
| `mat(1, 2; 3, 4)` | matrix; rows separated by `;` |
| `dot`, `times`, `<=`, `>=`, `!=`, `approx`, `->`, `in`, `infinity` | operators and symbols |
| `"ReLU"(x)`, `"if" x > 0` | words go in quotes |
| `a quad b` | wide space between two statements on one line |
| `x^top`, `det(A)`, `log`, `sin`, `max` | transpose and named operators |

A single letter is a variable; several letters together must be a known
name or be in quotes, so write `a b` for a times b, not `ab`. `$` and `#`
are not allowed. Keep to about 5 lines per object and keep lines short:
a wide line shrinks every line of that object.

### plot

Axes with curves and points.

```json
{ "id": "p", "type": "plot", "region": "left",
  "x": { "label": "w", "min": -1, "max": 7 },
  "y": { "label": "loss", "min": 0, "max": 16 },
  "curves": [ { "id": "f", "fn": "(x - 3)^2", "label": "f(w)", "visible": false },
              { "id": "data", "points": [[0, 1], [1, 0.6], [2, 0.4]] } ],
  "points": [ { "id": "w", "at": [0, 9], "label": "w₀" } ] }
```

A curve is a function of `x` (`fn`) or a line through data (`points`). A
function needs `x.min` and `x.max`. Give `y.min` and `y.max` too, so the axes
stay still. Functions use numbers, `x`, `pi`, `e`, `+ - * / ^`, parentheses,
and `sin cos tan exp ln log log2 sqrt abs tanh sigmoid relu floor`; `2x` and
`3(x - 1)` work. Parts: `p.f`, `p.w` (curves and points share one set of ids).
Set `"equal": true` when geometry matters (perpendicular lines, distances,
projections): both axes then use the same scale. Curves are clipped to the
axis ranges. Points on the same spot share one label.

| Action | Fields |
| --- | --- |
| `trace` | `target` (a curve declared with `"visible": false`); draws it |
| `move_to` | `target` (a point), `at: [x, y]` |
| `add_point` | `target` (the plot), `id`, `at`, optional `label` |
| `set` | `target` a curve and `value` a new function (the curve morphs), or `target` a point and `value` its new label |
| `remove` | `target` (a curve or point) |

### timeline

Lanes over a shared time axis: scheduling charts, pipeline stages, protocol
exchanges.

```json
{ "id": "cpu", "type": "timeline", "region": "center",
  "lanes": ["P1", "P2"], "end": 10, "unit": "time (ms)", "now": 0,
  "blocks": [ { "id": "a", "lane": "P1", "start": 0, "end": 2, "label": "P1" } ],
  "messages": [ { "id": "syn", "from": "P1", "to": "P2", "at": 1, "arrive": 2, "label": "SYN" } ] }
```

Give `end` so the axis does not stretch as blocks are added. Blocks in one
lane may not overlap. Parts: `cpu.a` (a block or message id) or `cpu.P1` (a
lane).

| Action | Fields |
| --- | --- |
| `add_block` | `target` (the timeline), `id`, `lane`, `start`, `end`, optional `label` |
| `add_message` | `target` (the timeline), `id`, `from`, `to`, `at`, optional `arrive`, `label` |
| `advance` | `target` (the timeline), `to` (moves the "now" cursor) |
| `set` | `target` (a block or message), `value` (its label) |
| `remove` | `target` (a block or message) |

A timeline needs width: put it in `center`, alone.

### space

Three-dimensional scenes: axes with points, vectors, planes, surfaces and
paths, seen through a camera that can orbit. `z` is up. Use it for what a
flat picture cannot show: PCA or SVD in three dimensions, a loss surface and
gradient descent on it, partial derivatives, projections onto a plane,
cross products, convolution volumes.

```json
{ "id": "sp", "type": "space", "region": "center",
  "axes": { "x": [-3, 3], "y": [-3, 3], "z": [-3, 3], "labels": ["x", "y", "z"], "grid": "xy" },
  "camera": { "azimuth": 35, "elevation": 24 },
  "parts": [
    { "kind": "point", "id": "a", "at": [2, 1, 0.5], "label": "A" },
    { "kind": "vector", "id": "u", "to": [2, 1, 0], "label": "u", "color": "amber" },
    { "kind": "vector", "id": "v", "to": [-1, 2, 0], "label": "v" },
    { "kind": "plane", "id": "p", "span": ["u", "v"], "visible": false },
    { "kind": "surface", "id": "f", "fn": "x^2 - y^2", "visible": false },
    { "kind": "path", "id": "walk", "points": [[-2, 0, 4], [0, 0, 0], [2, 0, 4]], "visible": false },
    { "kind": "label", "id": "note", "at": [0, 0, 2.5], "text": "origin above" } ] }
```

Parts: `point` (`at`), `vector` (`to`, optional `from`), `plane` (`normal`
plus `size`, or `span` of two vector ids: the parallelogram they span),
`surface` (`fn` of `x` and `y`, same language as plots, over the axes'
ranges or its own `x` and `y`), `path` (`points`), `label` (`at`, `text`).
Every part may carry `label` and `color` (`amber`, `green`, `blue`, `pink`,
`purple`, `orange`, `muted`) and `"visible": false`, to be brought in later
with `trace`. Parts are addressed `sp.a`. Give the axes ranges that fit the
data; all three axes share one scale, so angles and lengths are true.
Pointers and arrows can attach to a part (`sp.a`). Keep a scene to a
handful of parts; a space object needs room, so put it in `center` alone or
beside one text or math object.

| Action | Fields |
| --- | --- |
| `orbit` | `target` (the space), any of `azimuth`, `elevation` (degrees), `distance`; the camera glides there over the step |
| `look` | `target` (the space), `at: [x, y, z]`; the camera turns to it |
| `trace` | `target` (a part declared with `"visible": false`); a path draws itself, anything else appears |
| `add_point` | `target` (the space), `id`, `at: [x, y, z]`, optional `label` |
| `add_vector` | `target` (the space), `id`, `to`, optional `from`, `label`, `color` |
| `add_plane` | `target` (the space), `id`, `normal` + `size` or `span`, optional `through`, `label` |
| `move_to` | `target` (a point, a label, or a vector whose tip moves), `at: [x, y, z]` |
| `set` | `target` a surface and `value` a new function (it morphs), or any other part and `value` its new label text |
| `project` | `target` (a point or vector), `onto` (a plane or vector id), `id`: the projected copy appears with a thin drop line (`id_drop`) |
| `rotate` | `target` (a part, or the space for everything but surfaces), `about` (`x`, `y` or `z`), `degrees` |
| `span` | `target` (the space), `a`, `b` (vector ids), `id`: the parallelogram they span |
| `remove` | `target` (a part) |

Say what the viewer should look at before orbiting, and orbit slowly: one
`orbit` per step, 60 to 120 degrees at most. A projection reads best with
the camera low (`elevation` 15 to 25) so the drop lines are visible.

## Checking your work

1. `validate`: fix every error. Each one gives the path in the script and
   the reason. Read warnings too: an action on a hidden object, an object
   that is never shown and a sentence that is too long are usually mistakes.
2. `frame` with captions on, at the end of each scene and at the busiest
   steps: check that nothing overlaps, that text is large enough to read,
   and that the highlighted thing is the thing the sentence talks about.
3. Check every number on screen against the narration and against the
   actual computation. The renderer checks that a script is well formed, not
   that the mathematics in it is right.
4. `render`.

## Common mistakes

- Forgetting `show`: the object exists but never appears (a warning says so).
- Showing a new object in a region without hiding the old one, so both
  squeeze into half the space.
- Using `center` together with `left` or `right`.
- Writing LaTeX (`\frac{a}{b}`) in a math line instead of Typst (`a / b`).
- Writing `ab` in math for a product; write `a b`.
- A range that stops one short: `arr[0..3]` is cells 0, 1, 2.
- Removing an array cell or a node that a pointer still points at.
- Putting a whole derivation in one math object; use one object per scene.
