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
        grid-template-rows: 184px 42px minmax(0, 1fr);
        margin: 0 auto;
        padding: 10px 0;
        box-sizing: border-box;
      }

      /* Identity has presence, but the statistics remain the product. */
      .${styles.hero} {
        display: grid;
        height: 184px;
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
        padding: 0 0 4px;
      }

      .${styles.eyebrow} {
        margin-bottom: 4px;
        font-size: 0.57rem;
        letter-spacing: 0.16em;
      }

      .${styles.heroCopy} h1 {
        max-width: 100%;
        font-size: clamp(3.25rem, 3.85vw, 4.5rem);
        line-height: 0.9;
        letter-spacing: -0.055em;
      }

      .${styles.identityLine} {
        margin-top: 8px;
        font-size: 0.71rem;
      }

      .${styles.heroSummary} {
        display: -webkit-box;
        max-width: 520px;
        margin-top: 7px;
        overflow: hidden;
        font-size: 0.77rem;
        line-height: 1.3;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
      }

      .${styles.heroActions} {
        gap: 7px;
        margin-top: 9px;
      }

      .${styles.primaryAction},
      .${styles.secondaryAction} {
        min-height: 28px;
        padding: 0 11px;
        border-radius: 2px;
        font-size: 0.6rem;
      }

      /* Portrait is integrated into the masthead rather than floating above it. */
      .${styles.portraitStage} {
        position: relative;
        align-self: stretch;
        width: 100%;
        height: 184px;
        min-height: 0;
        overflow: hidden;
        contain: paint;
      }

      .${styles.portraitStage}::before {
        position: absolute;
        inset: 12% 12% -12%;
        border-radius: 50%;
        background: radial-gradient(circle at 50% 56%, rgba(118, 52, 48, 0.34), rgba(118, 52, 48, 0.1) 42%, transparent 72%);
        filter: blur(18px);
        content: "";
        pointer-events: none;
      }

      .${styles.portraitStage}::after {
        height: 34px;
        opacity: 0.92;
      }

      .${styles.portraitComposition} {
        position: absolute;
        z-index: 1;
        inset: 0;
        display: flex;
        align-items: flex-end;
        justify-content: center;
        overflow: hidden;
      }

      .${styles.portraitGlow} {
        right: 10%;
        bottom: -7px;
        width: 80%;
        max-height: 108%;
        opacity: 0.16;
        filter: blur(22px) saturate(0.68);
        transform: scale(1.05);
      }

      .${styles.portraitImage} {
        width: auto;
        height: 190px;
        max-width: 100%;
        max-height: 190px;
        object-fit: contain;
        object-position: bottom center;
        filter: saturate(0.91) contrast(1.015);
        transform: translateY(7px);
      }

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
        padding-bottom: 6px;
      }

      .${styles.railHeading} span,
      .${styles.railHeading} strong {
        font-size: 0.51rem;
      }

      .${styles.identityRail} dl {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        column-gap: 18px;
        row-gap: 0;
        margin-top: 5px;
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
        font-size: 0.59rem;
        text-align: right;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .${styles.crestLine} {
        gap: 6px;
        margin-top: 5px;
        font-size: 0.59rem;
      }

      .${styles.crestLine} img,
      .${styles.crestLine} svg {
        max-width: 31px;
        max-height: 31px;
      }

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

      /* Evidence still owns most of the viewport. */
      .${styles.workspace} {
        display: grid;
        height: 100%;
        min-height: 0;
        grid-template-rows: 68px minmax(0, 1fr);
        gap: 8px;
        padding-top: 8px;
        box-sizing: border-box;
      }

      .${styles.headlineGrid} {
        height: 68px;
        gap: 10px;
      }

      .${styles.headlineCard} {
        height: 68px;
        min-height: 0;
        padding: 7px 12px 6px;
        box-sizing: border-box;
        border-color: rgba(238, 229, 214, 0.085);
        border-radius: 2px;
        background: linear-gradient(145deg, rgba(30, 27, 26, 0.84), rgba(13, 14, 13, 0.86));
      }

      .${styles.headlineLabel} {
        font-size: 0.62rem;
      }

      .${styles.headlineCard} > div {
        gap: 9px;
        margin-top: 3px;
      }

      .${styles.headlineCard} strong {
        min-width: 47px;
        font-size: 1.48rem;
        line-height: 1;
      }

      .${styles.headlineBar} {
        height: 3px;
      }

      .${styles.headlineCard} small {
        margin-top: 2px;
        font-size: 0.5rem;
        line-height: 1.04;
      }

      /* Shared editorial grid: fingerprint + markers, evidence, context + discovery. */
      .${styles.overviewGrid} {
        display: grid;
        height: 100%;
        min-height: 0;
        grid-template-columns: var(--profile-columns);
        grid-template-rows: 104px minmax(0, 1fr) 84px;
        column-gap: 18px;
        row-gap: 8px;
        margin-top: 0;
        align-items: stretch;
      }

      .${styles.fingerprintPanel},
      .${styles.metricsPanel} {
        display: flex;
        min-height: 0;
        flex-direction: column;
        padding: 11px 14px 10px;
        box-sizing: border-box;
        border-color: rgba(238, 229, 214, 0.07);
        border-radius: 2px;
        background: rgba(10, 11, 10, 0.32);
      }

      .${styles.fingerprintPanel} {
        grid-column: 1;
        grid-row: 1 / 3;
      }

      .${styles.metricsPanel} {
        grid-column: 2;
        grid-row: 1 / 4;
      }

      .${styles.panelHeading} {
        flex: 0 0 auto;
        margin-bottom: 3px;
      }

      .${styles.panelHeading} p,
      .${styles.contextPanel} header p,
      .${styles.signalPanel} header p,
      .${styles.similarPanel} header p {
        font-size: 0.53rem;
        letter-spacing: 0.14em;
      }

      .${styles.panelHeading} h2,
      .${styles.contextPanel} h2,
      .${styles.similarPanel} h2 {
        font-size: 0.96rem;
      }

      /* Compact radar: visual orientation, not a full-column takeover. */
      .${styles.radar} {
        display: block;
        width: min(100%, 218px);
        height: auto;
        max-height: 202px;
        flex: 0 0 auto;
        margin: auto;
      }

      .${styles.radarLabel},
      .${styles.radarValue} {
        font-size: 8.3px;
      }

      /* FBref-like evidence, but denser and more editorial. */
      .${styles.metricsPanel} .${styles.metricRows} {
        display: grid;
        min-height: 0;
        flex: 1 1 auto;
        grid-auto-rows: 31px;
        align-content: start;
      }

      .${styles.metricsPanel} .${styles.metricRow} {
        min-height: 0;
        padding: 0;
      }

      .${styles.metricRow} {
        grid-template-columns: minmax(134px, 0.98fr) minmax(120px, 1.22fr) 36px;
        gap: 9px;
      }

      .${styles.metricName} span {
        font-size: 0.58rem;
      }

      .${styles.metricName} small {
        font-size: 0.5rem;
      }

      .${styles.metricRow} > strong {
        font-size: 0.57rem;
      }

      .${styles.metricBar} {
        height: 3px;
        background: rgba(238, 229, 214, 0.085);
      }

      .${styles.metricBar} > span {
        background: linear-gradient(90deg, #c9635b 0%, #ad8065 58%, #7f987c 100%);
        box-shadow: none;
      }

      /* Flatten the old right-stack wrapper so its governed modules can join the shared grid. */
      .${styles.contextStack} {
        display: contents;
      }

      .${styles.contextPanel} {
        grid-column: 3;
        grid-row: 1;
        min-height: 0;
        padding: 8px 11px 7px;
        border-color: rgba(238, 229, 214, 0.07);
        border-radius: 2px;
        background: rgba(10, 11, 10, 0.3);
      }

      .${styles.contextPanel} header {
        padding-bottom: 3px;
      }

      .${styles.contextPanel} dl {
        margin-top: 0;
      }

      .${styles.contextPanel} dl div {
        padding: 2px 0;
      }

      .${styles.contextPanel} dt,
      .${styles.contextPanel} dd {
        font-size: 0.54rem;
      }

      /* Existing Relative markers now complete the fingerprint column. */
      .${styles.signalPanel} {
        grid-column: 1;
        grid-row: 3;
        min-height: 0;
        padding: 7px 3px 5px;
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
        font-size: 0.47rem;
      }

      .${styles.signalRow} {
        padding: 1px 0;
      }

      .${styles.signalRow} span,
      .${styles.signalRow} strong {
        font-size: 0.51rem;
      }

      .${styles.similarPanel} {
        display: flex;
        grid-column: 3;
        grid-row: 2 / 4;
        min-height: 0;
        flex-direction: column;
        overflow: hidden;
        padding: 10px 11px 8px;
        border-color: rgba(238, 229, 214, 0.07);
        border-radius: 2px;
        background: rgba(10, 11, 10, 0.34);
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
