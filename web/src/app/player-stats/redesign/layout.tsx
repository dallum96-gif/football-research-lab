import type { ReactNode } from "react";
import styles from "./PlayerStatsRedesign.module.css";

export default function PlayerStatsRedesignLayout({ children }: { children: ReactNode }) {
  const desktopArtDirection = `
    @media (min-width: 1181px) and (min-height: 760px) {
      .${styles.inner} {
        padding: 14px 0 10px;
        grid-template-rows: 200px 46px minmax(0, 1fr);
      }

      .${styles.hero} {
        grid-template-columns: 0.92fr 1.13fr 0.76fr;
        gap: 10px;
        min-height: 200px;
      }

      .${styles.heroCopy} {
        padding: 4px 0 14px;
      }

      .${styles.heroCopy} h1 {
        font-size: clamp(3.7rem, 5.15vw, 5.9rem);
      }

      .${styles.portraitStage} {
        min-height: 200px;
      }

      .${styles.portraitImage} {
        width: min(100%, 420px);
        max-height: 116%;
      }

      .${styles.identityRail} {
        margin-bottom: 8px;
        padding-left: 14px;
      }

      .${styles.controlBar} {
        grid-template-columns: 0.92fr 1.13fr 0.76fr;
        gap: 10px;
        min-height: 46px;
      }

      .${styles.modeTabs} {
        grid-column: 1;
      }

      .${styles.controls} {
        grid-column: 2;
        align-items: center;
        justify-content: flex-end;
      }

      .${styles.sampleState} {
        grid-column: 3;
      }

      .${styles.workspace} {
        padding-top: 8px;
        grid-template-rows: 78px minmax(0, 1fr);
        gap: 8px;
      }

      .${styles.headlineCard} {
        min-height: 78px;
        height: 100%;
        box-sizing: border-box;
        padding: 9px 14px 7px;
      }

      .${styles.headlineCard} > div {
        margin-top: 5px;
      }

      .${styles.headlineCard} strong {
        font-size: 1.68rem;
      }

      .${styles.headlineCard} small {
        margin-top: 2px;
      }

      .${styles.overviewGrid} {
        grid-template-columns: 0.92fr 1.13fr 0.76fr;
        gap: 10px;
      }

      .${styles.fingerprintPanel},
      .${styles.metricsPanel} {
        padding: 11px 13px;
      }

      .${styles.panelHeading} {
        margin-bottom: 6px;
      }

      .${styles.contextStack} {
        grid-template-rows: auto auto minmax(112px, 1fr);
        gap: 6px;
      }

      .${styles.contextPanel} {
        padding: 8px 11px;
      }

      .${styles.contextPanel} header {
        padding-bottom: 4px;
      }

      .${styles.contextPanel} dl {
        margin-top: 2px;
      }

      .${styles.contextPanel} dl div {
        padding: 3px 0;
      }

      .${styles.signalPanel} {
        padding: 4px 2px 5px;
        border-right: 0;
        border-left: 0;
        border-radius: 0;
        background: transparent;
      }

      .${styles.signalPanel} header {
        padding-bottom: 2px;
        border-bottom: 0;
      }

      .${styles.signalPanel} h2 {
        font-size: 0.9rem;
      }

      .${styles.signalPanel} h3 {
        margin: 3px 0 1px;
      }

      .${styles.signalRow} {
        padding: 2px 0;
      }

      .${styles.similarPanel} {
        display: flex;
        min-height: 112px;
        flex-direction: column;
        overflow: visible;
        padding: 8px 11px 7px;
      }

      .${styles.similarPanel} header {
        padding-bottom: 4px;
      }

      .${styles.similarList} {
        display: grid;
        flex: 1;
        align-content: start;
      }

      .${styles.similarList} > a {
        min-height: 30px;
        padding: 4px 0;
      }

      .${styles.similarList} strong {
        font-size: 0.61rem;
      }

      .${styles.similarList} small {
        font-size: 0.52rem;
      }
    }
  `;

  return (
    <>
      <style>{desktopArtDirection}</style>
      {children}
    </>
  );
}
