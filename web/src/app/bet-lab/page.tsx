"use client";

import { useMemo, useState } from "react";
import styles from "./BetLab.module.css";

type CommonFraction = {
  numerator: number;
  denominator: number;
  label: string;
  decimal: number;
};

const COMMON_FRACTIONS: CommonFraction[] = [
  [1, 100], [1, 66], [1, 50], [1, 40], [1, 33], [1, 25], [1, 20], [1, 16], [1, 14], [1, 12],
  [1, 10], [1, 9], [1, 8], [1, 7], [1, 6], [1, 5], [2, 9], [1, 4], [2, 7], [3, 10], [1, 3],
  [4, 11], [2, 5], [4, 9], [1, 2], [8, 15], [4, 7], [8, 13], [2, 3], [8, 11], [4, 5], [5, 6],
  [10, 11], [1, 1], [11, 10], [6, 5], [5, 4], [11, 8], [6, 4], [13, 8], [7, 4], [15, 8], [2, 1],
  [9, 4], [5, 2], [11, 4], [3, 1], [10, 3], [7, 2], [4, 1], [9, 2], [5, 1], [6, 1], [7, 1],
  [8, 1], [9, 1], [10, 1], [12, 1], [14, 1], [16, 1], [20, 1], [25, 1], [33, 1], [40, 1],
  [50, 1], [66, 1], [100, 1],
].map(([numerator, denominator]) => ({
  numerator,
  denominator,
  label: numerator === denominator ? "EVS" : `${numerator}/${denominator}`,
  decimal: 1 + numerator / denominator,
})).sort((a, b) => a.decimal - b.decimal);

function parseFractionalOdds(value: string) {
  const cleaned = value.trim().toUpperCase().replace(/\s+/g, "");
  if (["EVS", "EVENS", "EVEN", "1/1"].includes(cleaned)) return 2;

  const match = cleaned.match(/^(\d+(?:\.\d+)?)\/(\d+(?:\.\d+)?)$/);
  if (!match) return null;

  const numerator = Number(match[1]);
  const denominator = Number(match[2]);
  if (!Number.isFinite(numerator) || !Number.isFinite(denominator) || numerator < 0 || denominator <= 0) return null;
  return 1 + numerator / denominator;
}

function nearestCommonPrice(decimalOdds: number) {
  return COMMON_FRACTIONS.reduce((best, candidate) =>
    Math.abs(candidate.decimal - decimalOdds) < Math.abs(best.decimal - decimalOdds) ? candidate : best
  );
}

function minimumCommonPrice(decimalOdds: number) {
  return COMMON_FRACTIONS.find((candidate) => candidate.decimal + 1e-9 >= decimalOdds) ?? null;
}

function formatPercent(value: number, digits = 1) {
  return `${value.toFixed(digits).replace(/\.0$/, "")}%`;
}

function formatDecimal(value: number) {
  return value.toFixed(2);
}

export default function BetLabPage() {
  const [probability, setProbability] = useState("75");
  const [offeredOdds, setOfferedOdds] = useState("1/2");
  const [haircut, setHaircut] = useState("3");
  const [minimumEdge, setMinimumEdge] = useState("5");

  const result = useMemo(() => {
    const probabilityNumber = Number(probability);
    const haircutNumber = Number(haircut);
    const minimumEdgeNumber = Number(minimumEdge);
    const offeredDecimal = parseFractionalOdds(offeredOdds);

    if (!Number.isFinite(probabilityNumber) || probabilityNumber <= 0 || probabilityNumber >= 100) {
      return { error: "Enter an FRL probability between 0% and 100%." } as const;
    }
    if (!Number.isFinite(haircutNumber) || haircutNumber < 0 || haircutNumber >= probabilityNumber) {
      return { error: "The safety haircut must be zero or more, and smaller than the FRL probability." } as const;
    }
    if (!Number.isFinite(minimumEdgeNumber) || minimumEdgeNumber < 0 || minimumEdgeNumber > 50) {
      return { error: "Enter a minimum edge between 0% and 50%." } as const;
    }

    const rawProbability = probabilityNumber / 100;
    const conservativeProbability = (probabilityNumber - haircutNumber) / 100;
    const fairDecimal = 1 / rawProbability;
    const conservativeFairDecimal = 1 / conservativeProbability;
    const minimumDecimal = (1 + minimumEdgeNumber / 100) / conservativeProbability;
    const fairPrice = nearestCommonPrice(fairDecimal);
    const thresholdPrice = minimumCommonPrice(minimumDecimal);

    if (offeredOdds.trim() && offeredDecimal == null) {
      return {
        error: "Use UK fractional odds such as 1/2, 4/5, 5/4, 2/1 or EVS.",
        probabilityNumber,
        haircutNumber,
        minimumEdgeNumber,
        conservativeProbability,
        fairDecimal,
        conservativeFairDecimal,
        minimumDecimal,
        fairPrice,
        thresholdPrice,
      } as const;
    }

    const impliedProbability = offeredDecimal ? 1 / offeredDecimal : null;
    const conservativeExpectedReturn = offeredDecimal
      ? conservativeProbability * offeredDecimal - 1
      : null;
    const decision = offeredDecimal
      ? (offeredDecimal + 1e-9 >= minimumDecimal ? "BET" : "PASS")
      : "ENTER PRICE";

    return {
      error: null,
      probabilityNumber,
      haircutNumber,
      minimumEdgeNumber,
      conservativeProbability,
      fairDecimal,
      conservativeFairDecimal,
      minimumDecimal,
      fairPrice,
      thresholdPrice,
      offeredDecimal,
      impliedProbability,
      conservativeExpectedReturn,
      decision,
    } as const;
  }, [probability, offeredOdds, haircut, minimumEdge]);

  const hasCoreResult = "fairDecimal" in result;
  const decision = "decision" in result ? result.decision : "CHECK INPUT";
  const thresholdLabel = hasCoreResult
    ? result.thresholdPrice?.label ?? `≥ ${formatDecimal(result.minimumDecimal)} decimal`
    : "—";

  return (
    <main className={styles.workspace}>
      <header className={styles.hero}>
        <div>
          <span>FRL BET LAB</span>
          <h1>Price the belief.</h1>
          <p>Give FRL an endorsed probability for the whole bet. Bet Lab turns it into fair odds, adds a safety margin, and tells you the minimum bookmaker price worth accepting.</p>
        </div>
        <div className={styles.heroRule}>
          <span>THE RULE</span>
          <strong>Probability first.<br />Price second.</strong>
          <p>For bet builders, enter a probability you actually endorse for the whole builder — not a naïve multiplication of correlated legs.</p>
        </div>
      </header>

      <section className={styles.calculator} aria-label="FRL bet price calculator">
        <div className={styles.inputsPanel}>
          <div className={styles.sectionHeading}>
            <span>01 · OUR VIEW</span>
            <strong>What do we think happens?</strong>
          </div>

          <label className={styles.field}>
            <span>FRL probability</span>
            <div className={styles.inputShell}>
              <input
                type="number"
                inputMode="decimal"
                min="1"
                max="99"
                step="0.5"
                value={probability}
                onChange={(event) => setProbability(event.target.value)}
                aria-describedby="probability-help"
              />
              <b>%</b>
            </div>
            <small id="probability-help">The probability we are prepared to put our name to for this selection or whole builder.</small>
          </label>

          <label className={styles.field}>
            <span>Bookmaker price</span>
            <div className={styles.inputShell}>
              <input
                type="text"
                inputMode="text"
                value={offeredOdds}
                onChange={(event) => setOfferedOdds(event.target.value)}
                placeholder="e.g. 4/5"
                aria-describedby="odds-help"
              />
              <b>FRAC</b>
            </div>
            <small id="odds-help">UK fractional odds: 1/2, 4/5, 5/4, 2/1 or EVS.</small>
          </label>

          <details className={styles.advanced}>
            <summary>Advanced discipline settings <span>+</span></summary>
            <div className={styles.advancedGrid}>
              <label className={styles.field}>
                <span>Safety haircut</span>
                <div className={styles.inputShell}>
                  <input
                    type="number"
                    inputMode="decimal"
                    min="0"
                    max="30"
                    step="0.5"
                    value={haircut}
                    onChange={(event) => setHaircut(event.target.value)}
                  />
                  <b>PTS</b>
                </div>
                <small>Reduces our probability to allow for model and judgement error.</small>
              </label>

              <label className={styles.field}>
                <span>Minimum edge wanted</span>
                <div className={styles.inputShell}>
                  <input
                    type="number"
                    inputMode="decimal"
                    min="0"
                    max="50"
                    step="1"
                    value={minimumEdge}
                    onChange={(event) => setMinimumEdge(event.target.value)}
                  />
                  <b>%</b>
                </div>
                <small>Extra expected return required above conservative break-even.</small>
              </label>
            </div>
          </details>

          {result.error && <p className={styles.error} role="alert">{result.error}</p>}
        </div>

        <aside className={styles.decisionPanel} data-decision={decision.toLowerCase().replace(" ", "-")} aria-live="polite">
          <span>FRL VERDICT</span>
          <strong>{decision}</strong>
          {hasCoreResult ? (
            <>
              <b>Minimum acceptable price: {thresholdLabel}</b>
              <p>
                {result.thresholdPrice
                  ? `${result.thresholdPrice.label} (${formatDecimal(result.thresholdPrice.decimal)} decimal) or better clears the FRL threshold.`
                  : `We need at least ${formatDecimal(result.minimumDecimal)} decimal odds.`}
              </p>
            </>
          ) : <p>Fix the inputs to calculate a price.</p>}
        </aside>
      </section>

      <section className={styles.outputs} aria-live="polite">
        <article>
          <span>FAIR PRICE</span>
          <strong>{hasCoreResult ? result.fairPrice.label : "—"}</strong>
          <small>{hasCoreResult ? `${formatDecimal(result.fairDecimal)} decimal · ${formatPercent(result.probabilityNumber)} raw probability` : "From the probability you entered"}</small>
        </article>

        <article>
          <span>PRICE IT AS</span>
          <strong>{hasCoreResult ? formatPercent(result.conservativeProbability * 100) : "—"}</strong>
          <small>{hasCoreResult ? `${formatPercent(result.probabilityNumber)} minus ${result.haircutNumber}pt safety haircut` : "Our conservative working probability"}</small>
        </article>

        <article className={styles.thresholdCard}>
          <span>FRL MINIMUM</span>
          <strong>{thresholdLabel}</strong>
          <small>{hasCoreResult ? `${formatDecimal(result.minimumDecimal)} exact decimal threshold · includes ${result.minimumEdgeNumber}% target edge` : "The price we refuse to go below"}</small>
        </article>

        <article>
          <span>BOOKMAKER IMPLIES</span>
          <strong>{"impliedProbability" in result && result.impliedProbability != null ? formatPercent(result.impliedProbability * 100) : "—"}</strong>
          <small>{"offeredDecimal" in result && result.offeredDecimal ? `${offeredOdds.toUpperCase()} = ${formatDecimal(result.offeredDecimal)} decimal` : "Enter a valid bookmaker price"}</small>
        </article>

        <article>
          <span>CONSERVATIVE EDGE</span>
          <strong>{"conservativeExpectedReturn" in result && result.conservativeExpectedReturn != null ? formatPercent(result.conservativeExpectedReturn * 100) : "—"}</strong>
          <small>Expected return per unit staked using the haircut probability and offered price.</small>
        </article>
      </section>

      <section className={styles.explainer}>
        <div className={styles.sectionHeading}>
          <span>02 · THE DISCIPLINE</span>
          <strong>Why the minimum is higher than fair odds</strong>
        </div>
        <div className={styles.mathStrip}>
          <div><span>FRL estimate</span><strong>{hasCoreResult ? formatPercent(result.probabilityNumber) : "—"}</strong></div>
          <i>→</i>
          <div><span>Safety haircut</span><strong>{hasCoreResult ? `−${result.haircutNumber} pts` : "—"}</strong></div>
          <i>→</i>
          <div><span>Price as</span><strong>{hasCoreResult ? formatPercent(result.conservativeProbability * 100) : "—"}</strong></div>
          <i>→</i>
          <div><span>Demand edge</span><strong>{hasCoreResult ? `${result.minimumEdgeNumber}%` : "—"}</strong></div>
          <i>→</i>
          <div><span>Only bet at</span><strong>{thresholdLabel}+</strong></div>
        </div>
        <p>The calculator does not decide the football probability. It disciplines the price after the analytical work is done. A BET verdict means the entered bookmaker odds clear your chosen threshold; it does not guarantee the selection will win or that the probability estimate is correct.</p>
      </section>
    </main>
  );
}
