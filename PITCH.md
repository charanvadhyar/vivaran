# Vivaran: every step, shown

**Great Indian AI Internship Challenge · built on Gnani AI · solo entry: Vadhyar Sai Charan, M.Tech CSE (AI & ML), VIT Vellore**

Live: [vivaran-kappa.vercel.app](https://vivaran-kappa.vercel.app) · Demo (2:33): [vivaran-gnani-demo.mp4](https://vivaran-kappa.vercel.app/pitch/vivaran-gnani-demo.mp4) · This page as PDF: [vivaran-pitch.pdf](platform/web/public/pitch/vivaran-pitch.pdf)

## Problem

Before semester finals, students revise from textbooks and notes that give the answer but skip the working. Lecturers teach in Telugu or Hindi mixed with English, yet most explanation videos are English only. A step-by-step animation takes hours to make, for every topic, so few exist.

## Solution

1. A student or teacher asks Claude or ChatGPT for a video. Through Vivaran's MCP connector the assistant writes a scene script to an exam standard: every symbol named, every number traced to where it came from.
2. Vivaran's own renderer (Rust) draws each step: tables, typeset maths, graphs, plots, timelines.
3. **Gnani Timbre** (v3.0) speaks every line in English, code-mixed Telugu or code-mixed Hindi. The picture is timed to the measured voice.
4. **Gnani Prisma** (v3.0, `codemix`) listens back to every clip and scores it against the script. Lines under 80% are flagged for a human before anything is published.

## Built on Gnani

- Timbre REST TTS: `language: auto` for mixed-script lines, numbers sent as words.
- Prisma REST STT: `format: codemix`, `te-IN,en-IN` hints, the script's terms as keyterms. Matching romanises Telugu and Devanagari, because Prisma sometimes writes English words in Indic letters.
- A real catch: Timbre read "P4" as "చార్" (Hindi for four) in a Telugu line. Names like P4 are now spelled out and checked again.

## Live today

- Banker's algorithm in English (6:27), Telugu (7:13) and Hindi (7:03), 53 steps each: 159 clips spoken by Timbre, 159 listened back by Prisma.
- Every video has chapters and a share panel (WhatsApp, LinkedIn, X, copy link).

## Who it is for

Engineering and MCA students before exams, starting with Telugu and Hindi speakers; and every student who understands a topic well: they connect Vivaran once, ask for a video, check each step and publish.

## Next

The rest of the exam set (page replacement, normalisation, Dijkstra, backpropagation), opening the connector to student creators, and more Indian languages through Timbre.

*Code map: `crates/` renderer (Rust) · `shell/` Gnani voice, listen-back and MCP server (Python; Gnani client in `shell/cevg_shell/gnani.py`) · `platform/` website (Next.js) · `examples/subjects/os_bankers.json` the Banker's algorithm script.*
