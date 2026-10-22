/** Join class names, skipping empties. */
export const cx = (...names: (string | false | null | undefined)[]) => names.filter(Boolean).join(" ");
