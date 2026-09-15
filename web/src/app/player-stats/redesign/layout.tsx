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
        --profile-columns: minmax(0, 0.88fr) minmax(0, 1.18fr) minmax(0, 0.78fr);
        display: grid;
        width: min(1500px, calc(100% - 64px));
        height: 100%;
        grid-template-rows: 158px 42px minmax(0, 1fr);
        margin: 0 auto;
        padding: 10px 0;
        box-sizing: border-box;
      }

      /* The masthead is orientation, not the product. */
      .${styles.hero} {
        display: grid;
        height: 158px;
        min-height: 0;
        grid-template-columns: var(--profile-columns);
        gap: 18px;
        align-items: stretch;
        overflow: hidden;
        border-bottom: 1px solid rgba(238, 229, 214, 0.11);
      }

      .${styles.heroCopy} {
        align-self: center;
        min-width: 0;
        padding: 0 0 2px;
      }

      .${styles.eyebrow} {
        margin-bottom: 4px;
        font-size: 0.57rem;
        letter-spacing: 0.16em;
      }

      .${styles.heroCopy} h1 {
        max-width: 100%;
        font-size: clamp(3.05rem, 3.55vw, 4.05rem);
        line-height: 0.9;
        letter-spacing: -0.055em;
      }

      .${styles.identityLine} {
        margin-top: 7px;
        font-size: 0.7rem;
      }

      .${styles.heroSummary} {
        display: -webkit-box;
        max-width: 500px;
        margin-top: 6px;
        overflow: hidden;
        font-size: 0.74rem;
        line-height: 1.28;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
      }

      .${styles.heroActions} {
        gap: 7px;
        margin-top: 8px;
      }

      .${styles.primaryAction},
      .${styles.secondaryAction} {
        min-height: 27px;
        padding: 0 10px;
        border-radius: 2px;
        font-size: 0.59rem;
      }

      /* Portrait becomes a quiet identity marker rather than a hero takeover. */
      .${styles.portraitStage} {
        position: relative;
        align-self: stretch;
        width: 100%;
        height: 158px;
        min-height: 0;
        overflow: hidden;
        contain: paint;
      }

      .${styles.portraitStage}::after {
        height: 24px;
        opacity: 0.78;
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
        right: 15%;
        bottom: -8px;
        width: 70%;
        max-height: 104%;
        opacity: 0.12;
        filter: blur(22px) saturate(0.65);
        transform: scale(1.04);
      }

      .${styles.portraitImage} {
        width: auto;
        height: 158px;
        max-width: 84%;
        max-height: 158px;
        object-fit: contain;
        object-position: bottom center;
        transform: translateY(1px);
      }

      /* Compact identity rail: useful context without competing with the analysis. */
      .${styles.identityRail} {
        position: relative;
        align-self: center;
        min-width: 0;
        margin: 0;
        padding: 0 0 0 16px;
        border-left: 1px solid rgba(238, 229, 214, 0.12);
      }

      .${styles.railHeading} {
        gap: 8px;
        padding-bottom: 5px;
      }

      .${styles.railHeading} span,
      .${styles.railHeading} strong {
        font-size: 0.5rem;
      }

      .${styles.identityRail} dl {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        column-gap: 18px;
        row-gap: 0;
        margin-top: 4px;
      }

      .${styles.identityRail} dl div {
        display: grid;
        grid-template-columns: auto minmax(0, 1fr);
        gap: 7px;
        padding: 2px 0;
        align-items: baseline;
      }

      .${styles.identityRail} dt {
        font-size: 0.49rem;
        letter-spacing: 0.07em;
      }

      .${styles.identityRail} dd {
        overflow: hidden;
        font-size: 0.58rem;
        text-align: right;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .${styles.crestLine} {
        gap: 6px;
        margin-top: 4px;
        font-size: 0.58rem;
      }

      .${styles.crestLine} img,
      .${styles.crestLine} svg {
        max-width: 30px;
        max-height: 30px;
      }

      /* One quiet utility strip between identity and evidence. */
      .${styles.controlBar} {
        display: grid;
        height: 42px;
        min-height: 42px;
        grid-template-columns: var(--profile-columns);
        gap: 18px;
        align-items: center;
        border-bottom: 1px solid rgba(238, 229, 214, 0.11);
      }

      .${styles.modeTabs} {
        grid-column: 1;
        align-self: stretch;
        gap: 22px;
      }

      .${styles.modeLink},
      .${styles.modeActive} {
        font-size: 0.66rem;
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
        font-size: 0.47rem;
        white-space: nowrap;
      }

      .${styles.seasonControl} select,
      .${styles.searchControl} input {
        height: 28px;
        border-radius: 2px;
      }

      .${styles.searchControl} {
        width: min(255px, 19vw);
      }

      .${styles.sampleState} {
        grid-column: 3;
        align-self: center;
        justify-self: end;
        font-size: 0.57rem;
        white-space: nowrap;
      }

      /* The analysis owns the page. */
      .${styles.workspace} {
        display: grid;
        height: 100%;
        min-height: 0;
        grid-template-rows: 72px minmax(0, 1fr);
        gap: 10px;
        padding-top: 10px;
        box-sizing: border-box;
      }

      .${styles.headlineGrid} {
        height: 72px;
        gap: 10px;
      }

      .${styles.headlineCard} {
        height: 72px;
        min-height: 0;
        padding: 8px 12px 7px;
        box-sizing: border-box;
        border-color: rgba(238, 229, 214, 0.085);
        border-radius: 2px;
        background: linear-gradient(145deg, rgba(30, 27, 26, 0.88), rgba(13, 14, 13, 0.88));
      }

      .${styles.headlineLabel} {
        font-size: 0.63rem;
      }

      .${styles.headlineCard} > div {
        gap: 10px;
        margin-top: 4px;
      }

      .${styles.headlineCard} strong {
        min-width: 48px;
        font-size: 1.52rem;
        line-height: 1;
      }

      .${styles.headlineBar} {
        height: 4px;
      }

      .${styles.headlineCard} small {
        margin-top: 2px;
        font-size: 0.51rem;
        line-height: 1.05;
      }

      .${styles.overviewGrid} {
        display: grid;
        height: 100%;
        min-height: 0;
        grid-template-columns: var(--profile-columns);
        gap: 18px;
        margin-top: 0;
        align-items: stretch;
      }

      .${styles.fingerprintPanel},
      .${styles.metricsPanel} {
        display: flex;
        height: 100%;
        min-height: 0;
        flex-direction: column;
        padding: 13px 15px 12px;
        box-sizing: border-box;
        border-color: rgba(238, 229, 214, 0.075);
        border-radius: 2px;
        background: rgba(10, 11, 10, 0.38);
      }

      .${styles.panelHeading} {
        flex: 0 0 auto;
        margin-bottom: 5px;
      }

      .${styles.panelHeading} p,
      .${styles.contextPanel} header p,
      .${styles.signalPanel} header p,
      .${styles.similarPanel} header p {
        font-size: 0.54rem;
        letter-spacing: 0.14em;
      }

      .${styles.panelHeading} h2,
      .${styles.contextPanel} h2,
      .${styles.similarPanel} h2 {
        font-size: 0.98rem;
      }

      .${styles.radar} {
        display: block;
        width: min(100%, 365px);
        height: auto;
        max-height: min(355px, calc(100% - 34px));
        flex: 1 1 auto;
        margin: auto;
      }

      .${styles.radarLabel} {
        font-size: 8.5px;
      }

      .${styles.radarValue} {
        font-size: 8.5px;
      }

      .${styles.metricsPanel} .${styles.metricRows} {
        display: grid;
        min-height: 0;
        flex: 1 1 auto;
        grid-auto-rows: minmax(0, 1fr);
      }

      .${styles.metricsPanel} .${styles.metricRow} {
        min-height: 0;
        padding: 0;
      }

      .${styles.metricRow} {
        grid-template-columns: minmax(138px, 1.02fr) minmax(110px, 1.18fr) 38px;
        gap: 10px;
      }

      .${styles.metricName} span {
        font-size: 0.6rem;
      }

      .${styles.metricName} small {
        font-size: 0.53rem;
      }

      .${styles.metricRow} > strong {
        font-size: 0.59rem;
      }

      /* Right rail reads as context -> interpretation -> discovery. */
      .${styles.contextStack} {
        display: grid;
        height: 100%;
        min-height: 0;
        grid-template-rows: 104px 78px minmax(0, 1fr);
        gap: 10px;
      }

      .${styles.contextPanel} {
        padding: 9px 11px 8px;
        border-color: rgba(238, 229, 214, 0.075);
        border-radius: 2px;
        background: rgba(10, 11, 10, 0.36);
      }

      .${styles.contextPanel} header {
        padding-bottom: 4px;
      }

      .${styles.contextPanel} dl {
        margin-top: 1px;
      }

      .${styles.contextPanel} dl div {
        padding: 2px 0;
      }

      .${styles.contextPanel} dt,
      .${styles.contextPanel} dd {
        font-size: 0.55rem;
      }

      .${styles.signalPanel} {
        padding: 6px 2px;
        border: 0;
        border-top: 1px solid rgba(238, 229, 214, 0.1);
        border-bottom: 1px solid rgba(238, 229, 214, 0.1);
        border-radius: 0;
        background: transparent;
      }

      .${styles.signalPanel} header {
        padding: 0;
        border: 0;
      }

      .${styles.signalPanel} header p {
        margin-bottom: 1px;
      }

      .${styles.signalPanel} h2 {
        font-size: 0.82rem;
      }

      .${styles.signalColumns} {
        gap: 18px;
      }

      .${styles.signalPanel} h3 {
        margin: 2px 0 0;
        font-size: 0.48rem;
      }

      .${styles.signalRow} {
        padding: 1px 0;
      }

      .${styles.signalRow} span,
      .${styles.signalRow} strong {
        font-size: 0.52rem;
      }

      .${styles.similarPanel} {
        display: flex;
        min-height: 0;
        flex-direction: column;
        overflow: hidden;
        padding: 10px 11px 8px;
        border-color: rgba(238, 229, 214, 0.075);
        border-radius: 2px;
        background: rgba(10, 11, 10, 0.4);
      }

      .${styles.similarPanel} header {
        flex: 0 0 auto;
        padding-bottom: 5px;
      }

      .${styles.similarList} {
        display: grid;
        min-height: 0;
        flex: 1 1 auto;
        grid-template-rows: repeat(3, minmax(0, 1fr));
      }

      .${styles.similarList} > a {
        min-height: 0;
        grid-template-columns: 30px minmax(0, 1fr) auto;
        gap: 9px;
        padding: 6px 0;
        align-items: center;
      }

      .${styles.similarList} strong {
        font-size: 0.63rem;
      }

      .${styles.similarList} small {
        font-size: 0.52rem;
      }

      .${styles.similarList} b {
        font-size: 0.76rem;
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
