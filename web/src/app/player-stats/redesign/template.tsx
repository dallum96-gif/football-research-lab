import type { ReactNode } from "react";
import styles from "./PlayerStatsRedesign.module.css";

export default function PlayerStatsRedesignTemplate({ children }: { children: ReactNode }) {
  const refinement = `
    @media (min-width: 1181px) and (min-height: 760px) {
      /* Let the portrait dissolve into the masthead rather than exposing a rectangular stage. */
      .${styles.portraitStage} {
        overflow: visible;
        contain: none;
      }

      .${styles.portraitComposition} {
        overflow: visible;
      }

      .${styles.portraitGlow} {
        display: none;
      }

      .${styles.portraitStage}::before {
        inset: -8% -20% -18%;
        border-radius: 50%;
        background: radial-gradient(
          ellipse at 50% 58%,
          rgba(112, 48, 45, 0.28) 0%,
          rgba(112, 48, 45, 0.13) 36%,
          rgba(31, 19, 18, 0.045) 58%,
          transparent 76%
        );
        filter: blur(20px);
      }

      .${styles.portraitStage}::after {
        right: -18%;
        left: -18%;
        height: 38px;
        background: linear-gradient(
          180deg,
          transparent 0%,
          rgba(16, 16, 15, 0.42) 48%,
          rgba(16, 16, 15, 0.94) 100%
        );
        opacity: 1;
      }

      .${styles.portraitImage} {
        -webkit-mask-image: linear-gradient(to bottom, #000 0%, #000 82%, rgba(0, 0, 0, 0.88) 90%, transparent 100%);
        mask-image: linear-gradient(to bottom, #000 0%, #000 82%, rgba(0, 0, 0, 0.88) 90%, transparent 100%);
        filter: saturate(0.92) contrast(1.015) drop-shadow(0 12px 24px rgba(0, 0, 0, 0.12));
      }

      /* Similar players are secondary discovery, not another analytical panel. */
      .${styles.similarPanel} {
        grid-column: 3;
        grid-row: 2;
        align-self: start;
        height: 172px;
        min-height: 172px;
        padding: 8px 10px 6px;
        border-right: 0;
        border-left: 0;
        border-radius: 0;
        background: transparent;
      }

      .${styles.similarPanel} header {
        padding-bottom: 4px;
      }

      .${styles.similarList} {
        display: grid;
        flex: 0 0 auto;
        grid-template-rows: repeat(3, 42px);
        min-height: 0;
      }

      .${styles.similarList} > a {
        min-height: 0;
        grid-template-columns: 24px minmax(0, 1fr) auto;
        gap: 8px;
        padding: 4px 0;
        align-items: center;
      }

      .${styles.similarList} strong {
        font-size: 0.61rem;
      }

      .${styles.similarList} small {
        font-size: 0.49rem;
      }

      .${styles.similarList} b {
        font-size: 0.72rem;
      }
    }
  `;

  return (
    <>
      <style>{refinement}</style>
      {children}
    </>
  );
}
