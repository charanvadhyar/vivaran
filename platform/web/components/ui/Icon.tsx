import type { SVGProps } from "react";

/* The icon set: 16 or 20 px, 1.6 stroke, round caps. Add a path here, not an icon library. */
const PATHS: Record<string, React.ReactNode> = {
  search: <><circle cx="7" cy="7" r="4.5" /><path d="M10.5 10.5 14 14" /></>,
  play: <path d="M4 2.5v11l9-5.5z" fill="currentColor" stroke="none" />,
  pause: <><path d="M4.5 2.5v11" /><path d="M11.5 2.5v11" /></>,
  copy: <><rect x="5.5" y="5.5" width="8" height="8" rx="1.5" /><path d="M10.5 5.5v-2a1 1 0 0 0-1-1h-6a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2" /></>,
  check: <path d="M3 8.5 6.5 12 13 4.5" />,
  x: <><path d="M4 4l8 8" /><path d="M12 4l-8 8" /></>,
  chevronRight: <path d="M6 3l5 5-5 5" />,
  chevronDown: <path d="M3 6l5 5 5-5" />,
  arrowRight: <><path d="M3 8h10" /><path d="M9 4l4 4-4 4" /></>,
  download: <><path d="M8 2.5v8" /><path d="M4.5 7 8 10.5 11.5 7" /><path d="M3 13.5h10" /></>,
  trash: <><path d="M3 4.5h10" /><path d="M6.5 4.5v-1a1 1 0 0 1 1-1h1a1 1 0 0 1 1 1v1" /><path d="M4.5 4.5l.6 8a1 1 0 0 0 1 .9h3.8a1 1 0 0 0 1-.9l.6-8" /></>,
  globe: <><circle cx="8" cy="8" r="5.5" /><path d="M2.5 8h11" /><path d="M8 2.5c2 2 2 9 0 11" /><path d="M8 2.5c-2 2-2 9 0 11" /></>,
  lock: <><rect x="3.5" y="7" width="9" height="6.5" rx="1.5" /><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0v2" /></>,
  volume: <><path d="M2.5 6v4h2.5l3 2.5v-9L5 6z" /><path d="M10.5 5.5a3.5 3.5 0 0 1 0 5" /></>,
  mute: <><path d="M2.5 6v4h2.5l3 2.5v-9L5 6z" /><path d="M10.5 6.5l3 3" /><path d="M13.5 6.5l-3 3" /></>,
  fullscreen: <><path d="M3 6V3h3" /><path d="M13 6V3h-3" /><path d="M3 10v3h3" /><path d="M13 10v3h-3" /></>,
  clock: <><circle cx="8" cy="8" r="5.5" /><path d="M8 5v3.5l2.5 1.5" /></>,
  eye: <><path d="M1.5 8s2.5-4.5 6.5-4.5S14.5 8 14.5 8 12 12.5 8 12.5 1.5 8 1.5 8z" /><circle cx="8" cy="8" r="2" /></>,
  spark: <path d="M8 2l1.5 4.5L14 8l-4.5 1.5L8 14l-1.5-4.5L2 8l4.5-1.5z" />,
  plus: <><path d="M8 3v10" /><path d="M3 8h10" /></>,
  refresh: <><path d="M13 8a5 5 0 1 1-1.5-3.5" /><path d="M13 2.5v3h-3" /></>,
  info: <><circle cx="8" cy="8" r="5.5" /><path d="M8 7.5v3.5" /><circle cx="8" cy="5.3" r="0.6" fill="currentColor" /></>,
  warning: <><path d="M8 2.5 14 13H2z" /><path d="M8 6.5v3" /><circle cx="8" cy="11.3" r="0.6" fill="currentColor" /></>,
  mic: <><rect x="6" y="2" width="4" height="7" rx="2" /><path d="M3.5 7.5a4.5 4.5 0 0 0 9 0" /><path d="M8 12v2" /></>,
  captions: <><rect x="2" y="3.5" width="12" height="9" rx="1.5" /><path d="M4.5 9.5h3" /><path d="M9 9.5h2.5" /><path d="M4.5 7h2" /></>,
  menu: <><path d="M3 4.5h10" /><path d="M3 8h10" /><path d="M3 11.5h10" /></>,
  sun: <><circle cx="8" cy="8" r="3" /><path d="M8 1.5v1.5M8 13v1.5M1.5 8H3M13 8h1.5M3.4 3.4l1 1M11.6 11.6l1 1M3.4 12.6l1-1M11.6 4.4l1-1" /></>,
  moon: <path d="M13 9.5A5.5 5.5 0 0 1 6.5 3a5.5 5.5 0 1 0 6.5 6.5z" />,
  share: <><circle cx="4" cy="8" r="1.8" /><circle cx="12" cy="3.8" r="1.8" /><circle cx="12" cy="12.2" r="1.8" /><path d="M5.6 7.1l4.8-2.4" /><path d="M5.6 8.9l4.8 2.4" /></>,
  link: <><path d="M6.8 9.2a2.5 2.5 0 0 0 3.5 0l2.2-2.2a2.5 2.5 0 0 0-3.5-3.5L8 4.5" /><path d="M9.2 6.8a2.5 2.5 0 0 0-3.5 0L3.5 9a2.5 2.5 0 0 0 3.5 3.5l1-1" /></>,
};

export type IconName = keyof typeof PATHS;

export function Icon({ name, size = 16, ...rest }: { name: IconName; size?: 16 | 20 | 24 } & SVGProps<SVGSVGElement>) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.6"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden focusable="false" {...rest}>
      {PATHS[name]}
    </svg>
  );
}
