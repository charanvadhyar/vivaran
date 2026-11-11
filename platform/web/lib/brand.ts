export const BRAND = {
  name: "Vivaran",
  native: "వివరణ · विवरण",
  tagline: "Every step, shown.",
  // Where people write about their data, the terms, or a video. Shown on /privacy and /terms.
  contact: "charanvadhyar@gmail.com",
  owner: "Vadhyar Sai Charan",
  description:
    "Step-by-step animated explanations of computer science and mathematics, in English, Telugu and Hindi. See where every number comes from, so you can redo it in the exam.",
};

// Keep in step with SUBJECTS in shell/cevg_shell/hosted.py.
export const SUBJECTS: { id: string; name: string; short: string }[] = [
  { id: "dsa", name: "Data Structures & Algorithms", short: "DSA" },
  { id: "ml", name: "Machine Learning", short: "ML" },
  { id: "dbms", name: "Databases", short: "DBMS" },
  { id: "os", name: "Operating Systems", short: "OS" },
  { id: "coa", name: "Computer Architecture", short: "COA" },
  { id: "networks", name: "Computer Networks", short: "Networks" },
  { id: "maths", name: "Mathematics", short: "Maths" },
  { id: "other", name: "Other", short: "Other" },
];

export const subjectName = (id: string | null | undefined) => SUBJECTS.find((s) => s.id === id)?.name ?? null;
export const subjectShort = (id: string | null | undefined) => SUBJECTS.find((s) => s.id === id)?.short ?? null;
