import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { TeamKit } from "./teams/TeamKit";

const kits = [
  "Arsenal",
  "Liverpool",
  "Manchester City",
  "Aston Villa",
  "Chelsea",
  "Newcastle United",
  "Tottenham Hotspur",
  "Brighton and Hove Albion",
];

export default function HomePage() {
  return (
    <AppShell>
      <style>{`
        .home {
          display: grid;
          gap: 14px;
          width: 100%;
          max-width: 1320px;
        }

        .hero {
          min-height: 530px;
          display: grid;
          grid-template-columns: minmax(0, 1fr) minmax(420px, .92fr);
          overflow: hidden;
          background: #fffdf8;
          border: 1px solid rgba(23,23,20,.10);
          border-radius: 24px;
        }

        .hero-copy {
          display: flex;
          flex-direction: column;
          justify-content: center;
          padding: clamp(40px, 5vw, 72px);
        }

        .kicker {
          margin: 0 0 10px;
          color: #e85d3f;
          font-size: 10px;
          font-weight: 850;
          letter-spacing: .16em;
          text-transform: uppercase;
        }

        .hero h1 {
          margin: 0;
          max-width: 650px;
          font-size: clamp(52px, 6vw, 84px);
          line-height: .9;
          letter-spacing: -.075em;
        }

        .hero h1 em {
          color: #e85d3f;
          font-family: Georgia, serif;
          font-weight: 500;
        }

        .hero-copy > p:not(.kicker) {
          max-width: 550px;
          margin: 25px 0 0;
          color: #68645c;
          font-size: 14px;
          line-height: 1.6;
        }

        .actions {
          display: flex;
          gap: 9px;
          margin-top: 28px;
        }

        .actions a {
          display: inline-flex;
          align-items: center;
          gap: 20px;
          min-height: 44px;
          padding: 0 18px;
          border-radius: 99px;
          text-decoration: none;
          font-size: 11px;
          font-weight: 800;
        }

        .actions a:first-child {
          background: #1b1b18;
          color: #fffdf8;
        }

        .actions a:first-child span {
          color: #e85d3f;
          font-size: 17px;
        }

        .actions a:last-child {
          border: 1px solid rgba(23,23,20,.20);
        }

        .tiny-note {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-top: auto;
          padding-top: 35px;
          color: #68645c;
          font-size: 9px;
          font-weight: 700;
        }

        .tiny-note i {
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: #9aaa42;
        }

        .kit-board {
          position: relative;
          display: flex;
          flex-direction: column;
          padding: 28px;
          background:
            radial-gradient(circle at 100% 0%, rgba(232,93,63,.65), transparent 42%),
            radial-gradient(circle at 0% 100%, rgba(154,170,66,.62), transparent 43%),
            #24241f;
          color: #fffdf8;
        }

        .kit-board header span {
          display: block;
          color: rgba(255,253,248,.52);
          font-size: 8px;
          font-weight: 800;
          letter-spacing: .14em;
          text-transform: uppercase;
        }

        .kit-board header strong {
          display: block;
          margin-top: 3px;
          font-size: 12px;
        }

        .kits {
          flex: 1;
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          align-content: center;
          gap: 11px;
          padding: 22px 0;
        }

        .kit-card {
          aspect-ratio: 1;
          display: grid;
          place-items: center;
          padding: 12px;
          background: rgba(255,253,248,.94);
          border-radius: 20px;
          box-shadow: 0 14px 32px rgba(0,0,0,.18);
          transition: transform .18s ease;
        }

        .kit-card:nth-child(odd) { transform: rotate(-3deg); }
        .kit-card:nth-child(even) { transform: rotate(3deg); }
        .kit-card:nth-child(3) { transform: translateY(-8px) rotate(4deg); }
        .kit-card:nth-child(6) { transform: translateY(8px) rotate(-4deg); }

        .kit-card:hover {
          z-index: 2;
          transform: translateY(-5px) rotate(0deg) scale(1.06);
        }

        .kit-card > span,
        .kit-card svg {
          width: 100%;
          height: 100%;
        }

        .kit-caption {
          display: flex;
          justify-content: space-between;
          gap: 15px;
          padding: 12px 14px;
          background: rgba(255,253,248,.94);
          color: #171714;
          border-radius: 13px;
        }

        .kit-caption strong {
          font-size: 11px;
        }

        .kit-caption span {
          color: #68645c;
          font-size: 8px;
          text-align: right;
        }

        .explore {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 10px;
        }

        .tile {
          position: relative;
          min-height: 190px;
          display: flex;
          flex-direction: column;
          padding: 19px;
          overflow: hidden;
          border: 1px solid rgba(23,23,20,.09);
          border-radius: 18px;
          text-decoration: none;
          transition: transform .18s ease, box-shadow .18s ease;
        }

        .tile:hover {
          transform: translateY(-3px);
          box-shadow: 0 12px 26px rgba(23,23,20,.08);
        }

        .tile:nth-child(1) { background: #f2ded7; }
        .tile:nth-child(2) { background: #e4e7c8; }
        .tile:nth-child(3) { background: #dce7e7; }

        .tile small {
          font-size: 8px;
          font-weight: 850;
          letter-spacing: .12em;
          text-transform: uppercase;
        }

        .tile h2 {
          margin: auto 0 7px;
          font-size: 24px;
          letter-spacing: -.04em;
        }

        .tile p {
          max-width: 330px;
          margin: 0;
          color: #68645c;
          font-size: 9.5px;
          line-height: 1.5;
        }

        .tile b {
          position: absolute;
          right: 16px;
          bottom: 15px;
          display: grid;
          place-items: center;
          width: 30px;
          height: 30px;
          background: rgba(255,255,255,.72);
          border-radius: 50%;
        }

        .question {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 20px;
          padding: 15px 18px;
          background: #1b1b18;
          color: #fffdf8;
          border-radius: 15px;
        }

        .question span {
          color: #9aaa42;
          font-size: 8px;
          font-weight: 850;
          letter-spacing: .12em;
          text-transform: uppercase;
        }

        .question strong {
          font-family: Georgia, serif;
          font-size: 14px;
          font-weight: 500;
          font-style: italic;
          text-align: center;
        }

        .question a {
          color: #e85d3f;
          font-size: 9px;
          font-weight: 800;
          text-decoration: none;
          white-space: nowrap;
        }

        @media (max-width: 1000px) {
          .hero { grid-template-columns: 1fr; }
          .kit-board { min-height: 470px; }
        }

        @media (max-width: 720px) {
          .explore { grid-template-columns: 1fr; }
          .kits { grid-template-columns: repeat(4, 1fr); }
          .question {
            align-items: flex-start;
            flex-direction: column;
          }
          .question strong { text-align: left; }
        }
      `}</style>

      <div className="home">
        <section className="hero">
          <div className="hero-copy">
            <p className="kicker">Football Research Laboratory</p>

            <h1>
              Football data.
              <br />
              <em>Much less boring.</em>
            </h1>

            <p>
              Explore teams, matches, form and patterns without fighting
              your way through spreadsheet soup.
            </p>

            <div className="actions">
              <Link href="/teams">
                Pick a team <span>→</span>
              </Link>
              <Link href="/fixtures">Browse fixtures</Link>
            </div>

            <div className="tiny-note">
              <i />
              Built for curiosity, not mystery numbers.
            </div>
          </div>

          <div className="kit-board">
            <header>
              <span>FRL wardrobe</span>
              <strong>Pick a shirt. Find a rabbit hole.</strong>
            </header>

            <div className="kits">
              {kits.map((team) => (
                <div className="kit-card" title={team} key={team}>
                  <TeamKit teamName={team} />
                </div>
              ))}
            </div>

            <div className="kit-caption">
              <strong>Yes, the little kits are staying.</strong>
              <span>Completely unnecessary.<br />Completely correct.</span>
            </div>
          </div>
        </section>

        <section className="explore">
          <Link href="/teams" className="tile">
            <small>01 · Teams</small>
            <h2>Meet the clubs.</h2>
            <p>
              Seasons, records, XIs, fixtures and form — one proper
              football profile instead of fifty disconnected tables.
            </p>
            <b>→</b>
          </Link>

          <Link href="/fixtures" className="tile">
            <small>02 · Fixtures</small>
            <h2>Put a match under the microscope.</h2>
            <p>
              One fixture. Many questions. Slightly unreasonable
              levels of investigation encouraged.
            </p>
            <b>→</b>
          </Link>

          <Link href="/research" className="tile">
            <small>03 · Research</small>
            <h2>Get suspicious.</h2>
            <p>
              Is the form real? Does home advantage matter here?
              Is the season average quietly lying to us?
            </p>
            <b>→</b>
          </Link>
        </section>

        <section className="question">
          <span>Today&apos;s unnecessary football question</span>
          <strong>
            “Are they actually improving, or have they just played
            three rubbish sides?”
          </strong>
          <Link href="/research">Investigate →</Link>
        </section>
      </div>
    </AppShell>
  );
}
