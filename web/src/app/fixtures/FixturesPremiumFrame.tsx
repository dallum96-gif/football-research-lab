import type { ReactNode } from "react";
import styles from "./FixturesPremium.module.css";

export function FixturesPremiumFrame({ children }: { children: ReactNode }) {
  return <div className={styles.frame}>{children}</div>;
}
