/** Small formatters that are safe in the browser (no Node imports). */

export function minutes(seconds: number | null | undefined): string {
  if (!seconds) return "";
  const total = Math.round(seconds);
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`;
}

export const LANGUAGES: Record<string, string> = {
  en: "English", hi: "Hindi", te: "Telugu", ta: "Tamil", bn: "Bengali", gu: "Gujarati",
  kn: "Kannada", ml: "Malayalam", mr: "Marathi", pa: "Punjabi", od: "Odia",
};
