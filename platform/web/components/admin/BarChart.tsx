import styles from "./BarChart.module.css";

/** Bars by day, drawn as SVG on the server. `stack` adds a second series on top, in the accent colour. */
export function BarChart({ title, data, value, stack, format = (n) => String(Math.round(n)), total }:
  { title: string; data: Record<string, number | string>[]; value: string; stack?: { key: string; label: string };
    format?: (n: number) => string; total?: string }) {
  const w = 600, h = 140, pad = 2;
  const vals = data.map((d) => Number(d[value] ?? 0) + (stack ? Number(d[stack.key] ?? 0) : 0));
  const max = Math.max(1, ...vals);
  const bw = w / Math.max(1, data.length);
  const sum = data.reduce((s, d) => s + Number(d[value] ?? 0), 0);
  return (
    <figure className={styles.chart}>
      <figcaption className={styles.head}>
        <span>{title}</span>
        <strong>{total ?? format(sum)}</strong>
      </figcaption>
      <svg viewBox={`0 0 ${w} ${h}`} className={styles.svg} role="img" aria-label={`${title} per day`} preserveAspectRatio="none">
        {data.map((d, i) => {
          const a = Number(d[value] ?? 0), b = stack ? Number(d[stack.key] ?? 0) : 0;
          const ha = (a / max) * (h - 4), hb = (b / max) * (h - 4);
          return (
            <g key={String(d.day)}>
              <title>{`${d.day}: ${format(a)}${stack ? ` · ${stack.label} ${format(b)}` : ""}`}</title>
              <rect x={i * bw + pad} y={h - ha} width={Math.max(1, bw - pad * 2)} height={ha} className={styles.bar} />
              {stack && hb > 0 ? <rect x={i * bw + pad} y={h - ha - hb} width={Math.max(1, bw - pad * 2)} height={hb} className={styles.stack} /> : null}
            </g>
          );
        })}
      </svg>
      <div className={styles.axis}>
        <span>{String(data[0]?.day ?? "").slice(5)}</span>
        {stack ? <span className={styles.legend}><i className={styles.key} /> {stack.label}</span> : null}
        <span>{String(data[data.length - 1]?.day ?? "").slice(5)}</span>
      </div>
    </figure>
  );
}
