# Vivaran design system

How the site looks and why, and the rules for adding to it. The code is
the source of truth: tokens in `styles/tokens.css`, components under
`components/`, and every component shown live at `/design`.

## Principles

Borrowed from the systems that do this well (Khan Academy's Wonder
Blocks for education, Vercel's Geist for restraint) and bent to what
Vivaran is: a place where students check working, not a marketing site.

1. **Credible.** Clean structure, no clutter, exact numbers in tabular
   figures. A student should trust the page the way they trust a good
   textbook. No decoration that does not carry meaning.
2. **Empowering, not patronising.** Plain words, no mascots, no
   confetti. The student is short on time and here to learn one thing.
3. **One accent, used as punctuation.** Amber marks the one thing to
   look at (the primary action, the current step, the focus ring). If
   two things on a screen are amber, one of them is wrong.
4. **Paper, ink, one amber accent.** The site is light, like a textbook
   page; the videos are dark, like a board, and stand out as the content.
   Headings are set in a book serif, body text in Geist. The accent is the
   videos' amber, darkened to read on paper; the bright amber appears only
   as the highlighter stroke. Dark is a complete alternate for night
   reading, not the default.
5. **Readable in three scripts.** Type sizes and line heights are chosen
   so Telugu and Devanagari sit comfortably beside Latin at 16px.
6. **Works before JavaScript.** Search, sign-in, publish and delete are
   forms. Scripts add convenience (copy, toasts, the player), never the
   only path.

## Tokens

Two layers. **Primitives** (`--slate-1`, `--amber-5`) are raw values and
are never used in a component. **Semantic tokens** say what a value is
for, in three families and three strengths:

| Family | Subtle | Default | Strong |
| --- | --- | --- | --- |
| Background | `--bg-canvas` | `--bg-surface` | `--bg-raised`, `--bg-strong` (knockout) |
| Foreground | `--fg-subtle` | `--fg-default` | `--fg-muted` (secondary), `--fg-knockout` (on strong/accent) |
| Border | `--border-subtle` | `--border-default` | `--border-strong` |

Plus `--accent` (+ `-hover`, `-ink`, `-wash`, `-border`, and `-mark` for the
highlighter stroke), the status
colours `--positive`, `--negative`, `--info` with their `-ink` pairs, and
`--focus-ring`, a double ring that is visible on any background.

Spacing is a 4px scale (`--space-1` … `--space-16`). Radii: 6, 9, 12, 16
and pill. Type: a scale from `--text-xs` (12px) to `--text-4xl` (44px);
Geist Sans for text, Geist Mono for addresses, times and code, with Noto
fallbacks for Telugu and Devanagari. Motion: 120/180/320 ms, all of it
removed under `prefers-reduced-motion`.

Contrast: every foreground token and the accent pass 4.5:1 on `--bg-canvas`
and `--bg-surface` in both themes; `--fg-subtle` is for hints only, never
for anything the reader must read.

## Components

One component per file, with its stylesheet beside it as a CSS module.
A component owns its look completely: pages compose components and
never restyle them.

**Primitives** (`components/ui`): Button, IconButton, Icon, Input,
Select, Switch, Slider, Badge, Chip, Tabs, Card, Stat, Avatar, Tooltip,
Dialog, Toast, Skeleton, EmptyState, Alert, CopyField, ProgressBar,
Kbd, Divider, ThemeToggle.

**Layout** (`components/layout`): Container, Header, SearchBar, Footer,
PageHeader, Section.

**Video** (`components/video`): VideoCard, VideoGrid, SubjectChips,
Player, StepsPanel, PublishPanel, DeleteButton, RenderStatus,
ConnectorCard, HowTo, CreatorHeader.

Rules for a new component:

- It gets `Name.tsx` and `Name.module.css`, and an entry on `/design`.
- Props say what, not how: `tone="positive"`, never `color="green"`.
- Anything clickable is a `<button>` or `<a>`; anything that needs a
  name for a screen reader gets `aria-label`; focus is visible.
- Text sizes and colours come from tokens. A hard-coded hex or px value
  in a component is a bug, except inside the video thumbnail, which
  shows the renderer's own colours.
- Client components (`"use client"`) only when the component holds
  state or touches the DOM. Nothing under `components/` imports from
  `lib/db`.

## Page patterns

- **Home**: hero (only when nothing is filtered), subject chips, one
  shelf per subject with at most four cards and a "See all" link.
- **Watch**: player left, "In this video" right; below the player, the
  title, the meta line, and the creator's publish panel if it is theirs.
  The player's controls sit under the picture because the videos carry
  captions in the bottom band.
- **Dashboard**: stats in the page header, connector card and how-to
  side by side, then the creator's videos with state badges.
- **Empty states** always say what would fill them and offer the action.

## What is deliberately not here

No icon library, no CSS framework, no component library. The icon set is
a map of SVG paths; adding one is adding a path. This keeps the bundle
small and the look ours.
