/** The contact page's choices, shared by the form (in the browser) and the server. */

/** The support topic for asking us to lift or raise a limit on an account. */
export const LIMIT_TOPIC = "A limit on my account";

/** The limits someone can ask about, by the name used in links (`?topic=limit&limit=downloads`). */
export const LIMITS = {
  held: "My free credits are on hold",
  credits: "More credits",
  length: "Longer videos",
  downloads: "More downloads a day",
  figures: "More figures a month",
  seo: "More “Write it for me” drafts",
  other: "Another limit",
} as const;

export type LimitName = keyof typeof LIMITS;
export const isLimit = (l: string): l is LimitName => l in LIMITS;

/** Where to ask for a limit to be raised, for messages that tell people they hit one. */
export const limitLink = (site: string, limit: LimitName) => `${site.replace(/\/$/, "")}/contact?kind=support&topic=limit&limit=${limit}`;

/** What someone can write to us about, and the topics under each. */
export const KINDS = {
  sales: {
    label: "Sales: Pro, packs, or Vivaran for a college or team",
    topics: ["Pro for myself", "Credit packs", "A college or department", "A coaching centre", "A company or team", "Something else"],
  },
  grievance: {
    label: "A grievance or complaint",
    topics: ["A video is wrong or misleading", "A video uses my work or my likeness", "A video is offensive or unlawful", "My account or credits", "My personal data", "Something else"],
  },
  support: {
    label: "Help with my account or a video",
    topics: [LIMIT_TOPIC, "Signing in", "Credits or Pro", "Making a video", "The YouTube channel", "Something else"],
  },
  other: { label: "Something else", topics: [] as string[] },
} as const;

export type Kind = keyof typeof KINDS;
export const isKind = (k: string): k is Kind => k in KINDS;

/** The reference people quote back to us. */
export const ticket = (id: string | number) => `VIV-${String(id).padStart(5, "0")}`;

/** How many messages one network may send in a day. */
export const MESSAGES_PER_NETWORK_PER_DAY = 5;

/** Grievances are acknowledged within a day and settled within 15 days. */
export const GRIEVANCE_ACK_HOURS = 24;
export const GRIEVANCE_RESOLVE_DAYS = 15;

