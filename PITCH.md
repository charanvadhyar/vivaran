# Vivaran: exam explanations that show every step

**Great Indian AI Internship Challenge submission** · built on Gnani AI

**Participant:** Vadhyar Sai Charan, M.Tech CSE (AI & ML), VIT Vellore · solo entry

**Demo video (2½ min):** [vivaran-gnani-demo.mp4](https://vivaran-kappa.vercel.app/pitch/vivaran-gnani-demo.mp4) · **Live project:** [vivaran-kappa.vercel.app](https://vivaran-kappa.vercel.app) · [One-page PDF](PITCH.pdf)

## Problem

When students revise for semester exams, their textbooks and notes give the final answer but skip the working. Many students learn in a mix of Telugu or Hindi and English, the way their lecturers teach, but most explanation videos are in English only. Making a good step-by-step animated explanation takes hours for each topic, so for most exam topics none exists.

## Solution

Vivaran turns an explanation into a short animated video that **shows every step**: each number on screen is traced back to where it came from, and nothing is skipped. The narration is in **English, code-mixed Telugu or code-mixed Hindi**, the way lecturers really speak.

A student or teacher asks their AI assistant for a video on a topic. Vivaran draws each step, and Gnani's voice narrates it. Anyone who understands a topic can make a video without any animation skills, and every video can be shared with a batch in one tap.

## How Gnani AI is used

- **Gnani's voice (Timbre)** speaks every line of every video in English, code-mixed Telugu and code-mixed Hindi. The animation is timed to the voice, so each step appears exactly when it is spoken.
- **Gnani's listening AI (Prisma)** hears every spoken line back and compares it with the script. Any line the voice got wrong is flagged for a person to check before the video is published.
- The check found a real mistake on the first video: in a Telugu sentence, the voice read "P4" (process four) as the Hindi word for four. We changed how such names are sent to the voice and checked the line again.

## What we built

- A working website, free to watch: **vivaran-kappa.vercel.app**.
- **Banker's algorithm**, a common operating-systems exam question, worked step by step in three full videos: English, Telugu and Hindi, about seven minutes each.
- **159 narrated lines**, every one spoken by Gnani's voice and checked by Gnani's listening AI.
- A watch page for every video, with chapters to jump to any step and sharing to WhatsApp, LinkedIn and X.
- A 2½-minute demo video showing the problem, the solution, sharing and creating, narrated in all three languages by Gnani.

## Who it helps

- **Students revising for exams**, starting with engineering and MCA students who think in Telugu or Hindi.
- **Teachers** who want their explanation to reach students after class.
- **Students who understand a topic well** and want to explain it to others.

## Award categories it fits

**Mixed Vibes** (code-mixed Telugu and Hindi voice), **Main Character** (regional language), **Solo Ninja** (solo entry).
