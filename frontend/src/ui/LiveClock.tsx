import { useEffect, useState } from "react";

/** Updates every second — use in status bars (isolated re-renders). */
export function LiveClock() {
  const [t, setT] = useState(() => new Date().toLocaleString());
  useEffect(() => {
    const id = window.setInterval(() => setT(new Date().toLocaleString()), 1000);
    return () => window.clearInterval(id);
  }, []);
  return <span className="ez-doc-status-segment ez-doc-status-segment--time">{t}</span>;
}
