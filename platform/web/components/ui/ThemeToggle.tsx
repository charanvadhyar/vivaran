"use client";

import { useEffect, useState } from "react";
import { IconButton } from "./IconButton";

/** Light is the default; this remembers a viewer's choice of the dark alternate. */
export function ThemeToggle() {
  const [theme, setTheme] = useState<"dark" | "light">("light");
  useEffect(() => {
    try {
      const saved = localStorage.getItem("vivaran-theme");
      if (saved === "dark") { setTheme("dark"); document.documentElement.dataset.theme = "dark"; }
    } catch { /* storage may be unavailable */ }
  }, []);
  const flip = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    if (next === "dark") document.documentElement.dataset.theme = "dark"; else delete document.documentElement.dataset.theme;
    try { localStorage.setItem("vivaran-theme", next); } catch { /* ignore */ }
  };
  return <IconButton icon={theme === "dark" ? "sun" : "moon"} label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"} onClick={flip} />;
}
