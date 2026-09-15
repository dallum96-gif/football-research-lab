import type { ReactNode } from "react";
import styles from "./PlayerStatsRedesign.module.css";

export default function PlayerStatsRedesignLayout({ children }: { children: ReactNode }) {
  const desktopArtDirection = `
    @media (min-width: 1181px) and (min-height: 760px) {
      .${styles.page} {
        height: calc(100dvh - 106px);
        min-height: 0;
        overflow: hidden;
      }

      .${styles.inner} {
        --profile-columns: minmax(0, 0.9fr) minmax(0, 1.15fr) minmax(0, 0.78fr);
        display: grid;
        width: min(1500px, calc(100% - 64px));
        height: 100%;
        grid-template-rows: 220px 44px minmax(0, 1fr);
        margin: 0 auto;
        padding: 10px 0 8px;
        box-sizing: border-box;
      }

      .${styles.hero} {
        display: grid;
        height: 220px;
        min-height: 0;
        grid-template-columns: var(--profile-columns);
        gap: 16px;
        align-items: stretch;
        overflow: hidden;
        border-bottom: 1px solid rgba(238, 229, 214, 0.12);
      }

      .${styles.heroCopy} {
        align-self: center;
        min-width: 0;
        padding: 0 0 8px;
      }

      .${styles.eyebrow} {
        margin-bottom: 5px;
      }

      .${styles.heroCopy} h1 {
        max-width: 100%;
        font-size: clamp(3.65rem, 4.35vw, 5rem);
        line-height: 0.9;
      }

      .${styles.identityLine} {
        margin-top: 10px;
        font-size: 0.76rem;
      }

      .${styles.heroSummary} {
        max-width: 510px;
        margin-top: 8px;
        font-size: 0.82rem;
        line-height: 1.34;
      }

      .${styles.heroActions} {
        gap: 7px;
        margin-top: 10px;
      }

      .${styles.primaryAction},
      .${styles.secondaryAction} {
        min-height: 30px;
        padding: 0 12px;
        font-size: 0.65rem;
      }

      .${styles.portraitStage} {
        position: relative;
        align-self: stretch;
        width: 100%;
        height: 220px;
        min-height: 0;
        overflow: hidden;
        contain: paint;
      }

      .${styles.portraitStage}::after {
        height: 32px;
      }

      .${styles.portraitComposition} {
        position: absolute;
        inset: 0;
        display: flex;
        align-items: flex-end;
        justify-content: center;
        overflow: hidden;
      }

      .${styles.portraitGlow} {
        right: 8%;
        bottom: -2px;
        width: 84%;
        max-height: 100%;
        transform: scale(1.02);
      }

      .${styles.portraitImage} {
        width: auto;
        height: 218px;
        max-width: 100%;
        max-height: 218px;
        object-fit: contain;
        object-position: bottom center;
        transform: translateY(1px);
      }

      .${styles.identityRail} {
        align-self: center;
        min-width: 0;
        margin: 0;
        padding: 0 0 0 16px;
        border-left: 1px solid rgba(238, 229, 214, 0.14);
      }

      .${styles.railHeading} {
        padding-bottom: 6px;
      }

      .${styles.identityRail} dl {
        margin-top: 6px;
      }

      .${styles.identityRail} dl div {
        padding: 3px 0;
      }

      .${styles.crestLine} {
        margin-top: 5px;
      }

      .${styles.controlBar} {
        display: grid;
        height: 44px;
        min-height: 44px;
        grid-template-columns: var(--profile-columns);
        gap: 16px;
        align-items: center;
        border-bottom: 1px solid rgba(238, 229, 214, 0.12);
      }

      .${styles.modeTabs} {
        grid-column: 1;
        align-self: stretch;
        gap: 24px;
      }

      .${styles.modeLink},
      .${styles.modeActive} {
        font-size: 0.71rem;
      }

      .${styles.controls} {
        grid-column: 2;
        min-width: 0;
        align-items: center;
        justify-content: flex-end;
        gap: 7px;
      }

      .${styles.seasonControl},
      .${styles.searchControl} label {
        display: flex;
        align-items: center;
        gap: 7px;
      }

      .${styles.seasonControl} > span,
      .${styles.searchControl} label > span {
        margin: 0;
        white-space: nowrap;
      }

      .${styles.seasonControl} select,
      .${styles.searchControl} input {
        height: 29px;
      }

      .${styles.searchControl} {
        width: min(245px, 18vw);
      }

      .${styles.sampleState} {
        grid-column: 3;
        align-self: center;
        justify-self: end;
        white-space: nowrap;
      }

      .${styles.workspace} {
        display: grid;
        min-height: 0;
        grid-template-rows: 76px minmax(0, 1fr);
        gap: 8px;
        padding-top: 8px;
      }

      .${styles.headlineGrid} {
        height: 76px;
        gap: 10px;
      }

      .${styles.headlineCard} {
        height: 76px;
        min-height: 0;
        padding: 9px 13px 8px;
        box-sizing: border-box;
      }

      .${styles.headlineCard} > div {
        gap: 11px;
        margin-top: 5px;
      }

      .${styles.headlineCard} strong {
        min-width: 50px;
        font-size: 1.62rem;
        line-height: 1;
      }

      .${styles.headlineCard} small {
        margin-top: 3px;
        line-height: 1.05;
      }

      .${styles.overviewGrid} {
        display: grid;
        height: 100%;
        min-height: 0;
        grid-template-columns: var(--profile-columns);
        gap: 16px;
        margin-top: 0;
        align-items: stretch;
      }

      .${styles.fingerprintPanel},
      .${styles.metricsPanel} {
        display: flex;
        height: 100%;
        min-height: 0;
        flex-direction: column;
        padding: 11px 13px;
        box-sizing: border-box;
      }

      .${styles.panelHeading} {
        flex: 0 0 auto;
        margin-bottom: 4px;
      }

      .${styles.panelHeading} h2 {
        font-size: 1rem;
      }

      .${styles.radar} {
        display: block;
        width: min(100%, 345px);
        height: auto;
        max-height: min(310px, calc(100% - 34px));
        flex: 1 1 auto;
        margin: auto;
      }

      .${styles.metricsPanel} .${styles.metricRows} {
        display: grid;
        min-height: 0;
        flex: 1 1 auto;
        grid-auto-rows: minmax(0, 1fr);
      }

      .${styles.metricsPanel} .${styles.metricRow} {
        min-height: 0;
      }

      .${styles.metricRow} {
        grid-template-columns: minmax(132px, 1.08fr) minmax(95px, 1fr) 40px;
        gap: 9px;
      }

      .${styles.metricName} span {
        font-size: 0.62rem;
      }

      .${styles.contextStack} {
        display: grid;
        height: 100%;
        min-height: 0;
        grid-template-rows: 112px 66px minmax(0, 1fr);
        gap: 8px;
      }

      .${styles.contextPanel} {
        padding: 8px 11px 7px;
      }

      .${styles.contextPanel} header {
        padding-bottom: 4px;
      }

      .${styles.contextPanel} h2,
      .${styles.similarPanel} h2 {
        font-size: 0.98rem;
      }

      .${styles.contextPanel} dl {
        margin-top: 2px;
      }

      .${styles.contextPanel} dl div {
        padding: 3px 0;
      }

      .${styles.signalPanel} {
        padding: 6px 2px 5px;
        border-right: 0;
        border-left: 0;
        border-radius: 0;
        background: transparent;
      }

      .${styles.signalPanel} header {
        padding: 0;
        border: 0;
      }

      .${styles.signalPanel} header p {
        margin-bottom: 2px;
      }

      .${styles.signalPanel} h2 {
        font-size: 0.82rem;
      }

      .${styles.signalColumns} {
        gap: 16px;
      }

      .${styles.signalPanel} h3 {
        margin: 3px 0 0;
      }

      .${styles.signalRow} {
        padding: 1px 0;
      }

      .${styles.similarPanel} {
        display: flex;
        min-height: 0;
        flex-direction: column;
        overflow: hidden;
        padding: 9px 11px 8px;
      }

      .${styles.similarPanel} header {
        flex: 0 0 auto;
        padding-bottom: 4px;
      }

      .${styles.similarList} {
        display: grid;
        min-height: 0;
        flex: 1 1 auto;
        grid-template-rows: repeat(3, minmax(0, 1fr));
      }

      .${styles.similarList} > a {
        min-height: 0;
        grid-template-columns: 28px minmax(0, 1fr) auto;
        gap: 8px;
        padding: 4px 0;
        align-items: center;
      }

      .${styles.similarList} strong {
        font-size: 0.61rem;
      }

      .${styles.similarList} small {
        font-size: 0.52rem;
      }

      .${styles.similarList} b {
        font-size: 0.78rem;
      }

      .${styles.workspace}:has(.${styles.exploreHeader}),
      .${styles.workspace}:has(.${styles.compareHeader}) {
        grid-template-rows: auto minmax(0, 1fr) auto;
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
