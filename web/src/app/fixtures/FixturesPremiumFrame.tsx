import type { ReactNode } from "react";
import styles from "./FixturesPremium.module.css";

export function FixturesPremiumFrame({ children }: { children: ReactNode }) {
  return (
    <div className={styles.frame}>
      <input
        className={styles.refineToggle}
        id="fixtures-refine-toggle"
        type="checkbox"
        aria-hidden="true"
      />
      <label className={styles.refineTrigger} htmlFor="fixtures-refine-toggle">
        Refine ↗
      </label>
      <label className={styles.backdrop} htmlFor="fixtures-refine-toggle" aria-hidden="true" />
      {children}
      <label className={styles.refineClose} htmlFor="fixtures-refine-toggle">
        Close ×
      </label>
    </div>
  );
}
