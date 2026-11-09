import { Container } from "@/components/layout/Container";
import styles from "./page.module.css";

export const metadata = {
  title: "Pitch",
  description: "Vivaran: exam explanations that show every step, narrated in English, code-mixed Telugu and code-mixed Hindi by Gnani.",
};

/** The one-page solution pitch for the Gnani AI challenge, with the demo. Prints on one page. */
export default function Pitch() {
  return (
    <Container main narrow>
      <article className={styles.page}>
        <header className={styles.head}>
          <p className={styles.kicker}>Great Indian AI Internship Challenge · built on Gnani AI</p>
          <h1>Vivaran: every step, <span className={styles.mark}>shown</span>.</h1>
          <p className={styles.lead}>Exam explanations as animated videos that trace every number to where it came from, narrated in
            English, code-mixed Telugu and code-mixed Hindi by Gnani Timbre, and checked line by line by Gnani Prisma.</p>
        </header>

        <video className={styles.video} controls preload="metadata" poster="/pitch/vivaran-demo.jpg" src="/pitch/vivaran-gnani-demo.mp4" />
        <p className={styles.links}>
          <a href="/pitch/vivaran-gnani-demo.mp4">Demo, 2:33</a> · <a href="/">Live site</a> · <a href="/explore?subject=os">Banker&apos;s algorithm in three languages</a> · <a href="/pitch/vivaran-pitch.pdf">This page as PDF</a>
        </p>

        <section>
          <h2>Problem</h2>
          <p>Before semester finals, students revise from textbooks and notes that give the answer but skip the working.
            Lecturers teach in Telugu or Hindi mixed with English, yet most explanation videos are English only, and a
            step-by-step animation takes hours to make for every topic.</p>
        </section>

        <section>
          <h2>Solution</h2>
          <ol>
            <li>A student or teacher asks Claude or ChatGPT for a video. Through Vivaran&apos;s connector (MCP) the assistant writes
              a scene script to an exam standard: every symbol named, every number traced, every decision said out loud.</li>
            <li>Vivaran&apos;s own renderer (Rust) draws each step: tables, typeset maths, graphs, plots, timelines.</li>
            <li><strong>Gnani Timbre</strong> speaks every line (Timbre v3.0; the library uses Vasudha, this demo Lakshmi) in English or code-mixed Telugu and Hindi;
              the picture is timed to the measured voice.</li>
            <li><strong>Gnani Prisma</strong> listens back to every clip (Prisma v3.0, codemix) and scores it against the script; lines
              under 80% are flagged for a human before anything is published.</li>
          </ol>
        </section>

        <section className={styles.two}>
          <div>
            <h2>Built on Gnani</h2>
            <ul>
              <li>Timbre REST TTS, <code>language: auto</code> for mixed-script lines, numbers sent as words.</li>
              <li>Prisma REST STT, <code>format: codemix</code>, <code>te-IN,en-IN</code> hints, the script&apos;s terms as keyterms.</li>
              <li>A real catch: Timbre read “P4” as “చార్” (Hindi four) in Telugu. Names are now spelled out and re-checked.</li>
            </ul>
          </div>
          <div>
            <h2>Live today</h2>
            <ul>
              <li>Banker&apos;s algorithm in English (6:27), Telugu (7:13) and Hindi (7:03), 53 steps each.</li>
              <li>159 clips spoken by Timbre, 159 listened back by Prisma.</li>
              <li>Every video has chapters and a share panel (WhatsApp, LinkedIn, X).</li>
            </ul>
          </div>
        </section>

        <section className={styles.two}>
          <div>
            <h2>Who it is for</h2>
            <p>Engineering and MCA students before exams, starting with Telugu and Hindi speakers; and every student who
              understands a topic well and wants to explain it: they connect Vivaran once, ask for a video, check each step, publish.</p>
          </div>
          <div>
            <h2>Next</h2>
            <p>The rest of the exam set (page replacement, normalisation, Dijkstra, backpropagation), opening the connector to
              student creators, and more Indian languages through Timbre.</p>
          </div>
        </section>

        <footer className={styles.foot}>Vadhyar Sai Charan · M.Tech CSE (AI &amp; ML), VIT Vellore · solo entry · vivaran-kappa.vercel.app</footer>
      </article>
    </Container>
  );
}
