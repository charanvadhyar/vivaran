import { Container } from "@/components/layout/Container";
import styles from "./page.module.css";

export const metadata = {
  title: "Pitch",
  description: "Vivaran: every student learns by making videos that teach others, in their own Indian language. Built on Gnani AI.",
};

/** The one-page submission for the Gnani AI challenge, with the demo. Same text as PITCH.md; prints on one page. */
export default function Pitch() {
  return (
    <Container main narrow>
      <article className={styles.page}>
        <header className={styles.head}>
          <p className={styles.kicker}>Great Indian AI Internship Challenge submission · built on Gnani AI</p>
          <h1>Vivaran: every student learns by making videos that <span className={styles.mark}>teach others</span>, in their own Indian language</h1>
          <p className={styles.byline}>Vadhyar Sai Charan, M.Tech CSE (AI &amp; ML), VIT Vellore · solo entry</p>
        </header>

        <video className={styles.video} controls preload="metadata" poster="/pitch/vivaran-demo.jpg" src="/pitch/vivaran-gnani-demo.mp4" />
        <p className={styles.links}>
          <a href="https://www.youtube.com/watch?v=MOc8587YlkA">Demo on YouTube, 2:33</a> · <a href="/">Live project</a> · <a href="/explore?subject=os">Banker&apos;s algorithm in three languages</a> · <a href="/pitch/vivaran-pitch.pdf">This page as PDF</a> · <a href="https://github.com/charanvadhyar/vivaran">Code</a>
        </p>

        <section>
          <h2>Problem</h2>
          <p>Across India, students learn in their own language mixed with English: Telugu, Tamil, Kannada, Malayalam, Marathi,
            Bengali, Gujarati, Punjabi, Hindi. That is how their lecturers teach. But almost all good explanation videos are in
            English, and textbooks give the final answer while skipping the working.</p>
          <p>Students already learn best by explaining: working a topic out step by step, so that a friend can follow it, is how
            it really sinks in. But turning an explanation into a step-by-step animated video takes hours and animation skills, so
            students never get to learn this way, and their explanations never reach anyone beyond their own group.</p>
        </section>

        <section>
          <h2>Solution</h2>
          <p><strong>With Vivaran, every student can create an educational video, in their own language, and learn by making it.</strong>{" "}
            A student picks a topic, even one they are still learning, and asks their AI assistant for a video. Vivaran draws every
            step, and Gnani&apos;s voice narrates it in English or in an Indian language mixed with English, the way students really
            talk. Before publishing, the student checks every step, and checking each step is where the learning happens. No
            animation skills, no recording studio, no editing.</p>
          <p>Every video <strong>shows every step</strong>: each number on screen is traced back to where it came from, and nothing
            is skipped. And every video is made to be shared: one tap to WhatsApp, LinkedIn or X, with chapters so a friend can jump
            straight to the step they are stuck on.</p>
          <p>So every video teaches twice: the student who made it learns the topic, and every student who watches it learns too, in
            the language they think in.</p>
        </section>

        <section>
          <h2>How Gnani AI is used</h2>
          <ul>
            <li><strong>Gnani&apos;s voice (Timbre)</strong> narrates every line. Because Timbre speaks English and nine Indian
              languages, a video can be made in any of them, and code-mixed lines (an Indian language with English terms) sound
              natural. The animation is timed to the voice, so each step appears exactly when it is spoken.</li>
            <li><strong>Gnani&apos;s listening AI (Prisma)</strong> hears every spoken line back and compares it with the script. Any
              line the voice got wrong is flagged for the creator to check before the video is published, so quality does not
              depend on the creator&apos;s ear alone.</li>
          </ul>
        </section>

        <section className={styles.two}>
          <div>
            <h2>What we built</h2>
            <ul>
              <li>A working website, free to watch: <strong>vivaran-kappa.vercel.app</strong>.</li>
              <li>The first topic, <strong>Banker&apos;s algorithm</strong> (a common operating-systems exam question), made in three
                languages to show the same explanation crossing languages: English, code-mixed Telugu and code-mixed Hindi, about
                seven minutes each.</li>
              <li><strong>159 narrated lines</strong>, every one spoken by Gnani&apos;s voice and checked by Gnani&apos;s listening AI.</li>
              <li>A watch page for every video, with chapters and one-tap sharing.</li>
            </ul>
          </div>
          <div>
            <h2>Who it helps</h2>
            <ul>
              <li><strong>Students who make videos</strong>, who learn a topic properly by explaining it step by step, in their own
                language, without animation skills.</li>
              <li><strong>Students who watch them</strong>, who get explanations in the language they think in, from people who
                learned it the same way.</li>
              <li><strong>Teachers</strong>, whose explanations can keep working after class.</li>
            </ul>
          </div>
        </section>
      </article>
    </Container>
  );
}
