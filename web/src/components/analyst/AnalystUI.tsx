"use client";

import { useEffect, useId, useRef, type ReactNode } from "react";
import styles from "./AnalystUI.module.css";

export function FormStrip({ results }: { results: string[] }) {
  return <div className={styles.form} aria-label={`Form: ${results.join(", ") || "unavailable"}`}>{results.length ? results.map((r, i) => <span key={i} data-result={r}>{r}</span>) : <small>No completed matches</small>}</div>;
}

export function RankBar({ label, percentile, rank, population, detail }: { label: string; percentile: number | null; rank?: number | null; population?: number | null; detail?: string }) {
  const available = percentile != null && Number.isFinite(percentile);
  return <div className={styles.rank}>
    <div><span>{label}</span><strong>{rank != null ? `#${rank}${population ? ` / ${population}` : ""}` : available ? `${Math.round(percentile)}th` : "—"}</strong></div>
    <div className={styles.track} role="img" aria-label={available ? `${label}: ${Math.round(percentile)} percentile` : `${label}: percentile unavailable`}><i style={{ width: available ? `${Math.max(0, Math.min(100, percentile))}%` : "0%" }} /></div>
    {detail && <small>{detail}</small>}
  </div>;
}

export function StatValue({ label, value, detail }: { label: string; value: ReactNode; detail?: string }) {
  return <div className={styles.stat}><span>{label}</span><strong>{value}</strong>{detail && <small>{detail}</small>}</div>;
}

export function PanelHeading({ eyebrow, title, action }: { eyebrow?: string; title: string; action?: ReactNode }) {
  return <div className={styles.heading}><div>{eyebrow && <small>{eyebrow}</small>}<h2>{title}</h2></div>{action}</div>;
}

export function CategoryTabs({ items, value, onChange, label = "Analysis category" }: { items: { id: string; label: string }[]; value: string; onChange: (id: string) => void; label?: string }) {
  return <div className={styles.tabs} role="group" aria-label={label}>{items.map(item => <button type="button" key={item.id} aria-pressed={value === item.id} onClick={() => onChange(item.id)}>{item.label}</button>)}</div>;
}

export function EvidenceDrawer({ open, onClose, title, children }: { open: boolean; onClose: () => void; title: string; children: ReactNode }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  useEffect(() => {
    const el = dialog.current;
    if (!el) return;
    if (open && !el.open) el.showModal();
    if (!open && el.open) el.close();
  }, [open]);
  return <dialog ref={dialog} className={styles.drawer} aria-labelledby={titleId} onCancel={onClose} onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
    <div className={styles.drawerInner}><header><div><small>FRL / Evidence desk</small><h2 id={titleId}>{title}</h2></div><button autoFocus onClick={onClose} aria-label="Close evidence">×</button></header><div className={styles.drawerBody}>{children}</div></div>
  </dialog>;
}
