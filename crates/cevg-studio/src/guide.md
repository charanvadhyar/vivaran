# Vivaran Studio: writing a 3D scene

A studio scene is one JSON document. It describes physical parts built from
parametric shapes, their materials, the camera, and narrated steps of
actions. It is rendered with a path tracer (real light, reflections, glow),
so it looks like a film, not a diagram. Units are metres; `z` is up.

Use Studio for machines and physical systems that must be seen to be
understood: a tokamak, a jet engine, a car engine, a cyclotron, a turbine, a
CPU package, an SSD, a transformer, a heat exchanger. Use the flat CEVG
script for algorithms, tables, maths and code.

The teaching standard still applies: name every part as it appears, say what
it does and why it is there, and show the order things happen in.

Never model a fictional or trademarked device (a film prop, a branded
product's exact design). Model the real engineering it is based on.

## Skeleton

```json
{
  "version": 1,
  "title": "How a tokamak holds a star in a magnetic bottle",
  "canvas": { "width": 1920, "height": 1080, "fps": 30, "samples": 128 },
  "environment": { "preset": "dark_studio" },
  "materials": {
    "steel": { "preset": "steel" },
    "plasma": { "preset": "emissive", "color": "#ff5bd1", "strength": 6 }
  },
  "parts": [
    { "id": "vessel", "shape": { "kind": "torus", "major": 2, "minor": 0.7, "angle": 270 }, "material": "steel", "label": "Vacuum vessel" }
  ],
  "camera": { "azimuth": -40, "elevation": 22, "distance": 11, "target": [0, 0, 0], "fov": 32 },
  "scenes": [
    { "id": "intro", "steps": [
      { "say": { "en": "This is the vacuum vessel." }, "do": [ { "action": "label", "target": "vessel" } ] }
    ] }
  ]
}
```

Every step has `say` (narration; `en` required, `hi` and `te` code-mixed as
in CEVG scripts) and `do` (actions). Actions stretch from their `delay` (a
fraction of the step, default 0) to the end of the step's narration, easing
in and out.

## Environment

| `preset` | Look |
| --- | --- |
| `dark_studio` | Near-black background, warm key, cool rim, soft fill. The teardown look; glowing parts read best. Default. |
| `studio` | Light grey, soft even light. For bright, clean product shots. |
| `black` | Pure black, one key light. For scenes lit mostly by their own glowing parts. |

`strength` scales the light; `background` (`#rrggbb`) changes the backdrop.
Without `lights`, the preset places its lights around the camera's target,
scaled to the scene. Give `lights` only for special effects:
`{ "id": "beam", "kind": "spot", "at": [0, 0, 5], "target": [0, 0, 0], "power": 800, "color": "#9fd0ff" }`
(`kind` is `area`, `point`, `spot` or `sun`; `size` for area lights).

## Materials

Each material starts from a `preset` and may override `color`, `metallic`,
`roughness` (0 mirror to 1 matte), `emission` (colour of light given off),
`strength` (brightness of that light: 1 faint, 5 to 15 bright, 20+ blinding),
`transmission` (0 to 1, for glass), `ior`, `opacity`. Colours are `#rrggbb`.

| Preset | Use |
| --- | --- |
| `steel`, `brushed_steel`, `aluminium`, `titanium`, `chrome` | structure, casings, shafts |
| `copper`, `brass`, `gold` | windings, contacts, conductors |
| `plastic`, `rubber`, `ceramic`, `paint` | housings, insulation, seals, painted parts (give `color`) |
| `glass` | windows, bulbs, lenses |
| `emissive` | plasma, filaments, LEDs, hot metal: `color` is the light's colour |

Keep emissive strengths modest (4 to 12); the bloom does the rest, and a
very bright part washes out to white and loses its colour.

## Parts

```json
{ "id": "coil", "shape": { ... }, "material": "copper",
  "at": [0, 0, 1.2], "rotate": [90, 0, 0], "scale": 1,
  "parent": "stator", "array": { ... }, "explode": [0, 0, 1],
  "visible": true, "label": "Field coil" }
```

`at` is the position relative to the parent, `rotate` is degrees about x,
then y, then z. A part without `shape` is a group: give sub-parts it as
`parent` and actions on the group act on all of them (show, hide, move,
explode, highlight). Parents must be declared before their children.
`label` is the name its callout shows. `explode` is the direction it moves
when its parent is exploded (default: away from the parent's centre).

### Shapes

| `kind` | Fields |
| --- | --- |
| `box` | `size: [x, y, z]`, `round` |
| `cylinder` | `radius`, `height`, `angle`, `round` (centred on its origin, axis z) |
| `tube` | `inner`, `outer`, `height`, `angle`, `start`, `round`: a pipe or ring |
| `cone` | `bottom`, `top`, `height` (radii; 0 for a point) |
| `sphere` | `radius` |
| `torus` | `major`, `minor`, `angle`, `start` |
| `revolve` | `profile: [[r, z], ...]`, `angle`, `start`, `closed` (default true), `round` |
| `extrude` | `outline: [[x, y], ...]`, `depth`, `round` (from z = 0 up) |
| `sweep` | `path` and `section` (below): wires, coils, pipes, frames |
| `gear` | `teeth`, `radius`, `depth`, optional `tooth` (height) and `bore` |

`angle` (degrees, default 360) makes a cutaway: a `revolve`, `tube`,
`cylinder` or `torus` with `"angle": 270` is missing a quarter, and the cut
faces are filled so the wall looks solid. Cut every concentric layer the
same way and put the camera in the missing quarter (azimuth between
`start + angle` and `start + 360`) to look inside.

`round` rounds every corner by that radius: 0.01 to 0.05 gives the small
bevels that make machined parts catch the light. Use it on most parts.

A `revolve` profile is a list of [r, z] points (r is the distance from the
z axis, at least 0) going round the cross-section. Points on the axis
(r = 0) close the shape at the centre: `[[0, -1], [1, -1], [1, 1], [0, 1]]`
is a cylinder.

Sweep paths:

| `path.kind` | Fields |
| --- | --- |
| `helix` | `radius`, `pitch` (rise per turn), `turns`: a coil about z starting at z = 0 |
| `circle` | `radius`: a ring in the xy plane |
| `arc` | `radius`, `angle`, `start` |
| `d_shape` | `inner`, `outer`, `height`: a tokamak field coil in the xz plane |
| `points` | `points: [[x, y, z], ...]`, `closed`, `smooth` (rounds the corners into a curve) |

Sections: `{ "kind": "circle", "radius": 0.03 }` or
`{ "kind": "rect", "width": 0.2, "height": 0.3, "round": 0.02 }`.

### Arrays

`"array": { "kind": "radial", "count": 12, "axis": "z", "angle": 360, "start": 0 }`
makes copies turned about the part's origin (a full circle spaces them
evenly; a partial `angle` runs from `start` to `start + angle`).
`"array": { "kind": "linear", "count": 5, "step": [0.3, 0, 0] }` makes copies
in a row. The copies are addressed `coil[0]`, `coil[1]`, ...; `coil` is all
of them.

## Actions

| Action | Fields | What happens |
| --- | --- | --- |
| `show` | `target`, optional `from: [x, y, z]` | fades in, sliding in from that offset if given |
| `hide` | `target`, optional `to` | fades out, sliding away by that offset if given |
| `move` | `target`, `to` or `by` | glides to a position (relative to its parent) or by an offset |
| `rotate` | `target`, `to` or `by` (degrees) | turns |
| `spin` | `target`, `axis`, `rpm` | keeps turning about its own axis until `stop` |
| `stop` | `target` | stops spinning |
| `explode` | `target`, `distance` | pulls the target's sub-parts (or an array's copies, outward) apart |
| `assemble` | `target` | puts them back |
| `glow` | `target`, `strength`, optional `color` | the part gives off light |
| `highlight` | `target` | the teaching highlight: a soft amber glow |
| `reset` | `target` | back to its material's own glow |
| `camera` | any of `azimuth`, `elevation`, `distance`, `target`, `fov` | the camera glides there |
| `focus` | `target`, optional `distance` | the camera aims at a part and frames it |
| `label` | `target`, optional `text` | a callout: a line from the part to its name |
| `unlabel` | `target` | removes the callout |

Parts start visible unless `"visible": false`. Callouts and captions are
drawn after rendering, so they are always sharp and never hidden by parts.

## Camera

`azimuth` is degrees from +x toward +y, `elevation` degrees above the xy
plane, `distance` metres from `target`. Move it on most steps, a little: a
slow drift of 10 to 20 degrees keeps a shot alive. Use one large move per
step at most, and say what to look at before you move to it. Keep
`elevation` between 10 and 40 for machines; lower makes them heroic, higher
makes the layout clear. `focus` is the easy way to go close to one part.

## Planning a video

1. Open on the whole machine, slowly closing in.
2. Cut it open (a cutaway made with `angle`), then go part by part from the
   outside in or from the input to the output: label, highlight, say what it
   does and why, reset, unlabel.
3. Explode it to show how the layers fit, then assemble.
4. End on the working machine: the thing that glows glows brightest, a slow
   orbit, the one-sentence summary.

About 7 steps a minute. Keep each part's highlight to its own step.

## Rendering

Rendering is paid and takes GPU time, so check the scene first: `validate`
reports every problem with its path; `preview` renders a few stills at half
size. The full render runs on the GPU servers and the creator is told when
it is ready.
