import Link from "next/link";
import { AppShell } from "@/components/AppShell";

const quickLinks = [
  { href: "/teams", index: "01", title: "Teams", note: "Profiles + form", tone: "olive" },
  { href: "/players", index: "02", title: "Players", note: "Profiles + output", tone: "blue" },
  { href: "/fixtures", index: "03", title: "Fixtures", note: "Schedule + results", tone: "sand" },
  { href: "/league-table", index: "04", title: "Table", note: "League position", tone: "rose" },
];

export default function HomePage() {
  return (
    <AppShell>
      <style>{`
        .home-workspace {
          height: calc(100dvh - 4.35rem);
          min-height: 0;
          display: grid;
          grid-template-rows: auto minmax(0, 1fr);
          gap: 12px;
          width: 100%;
          max-width: 1320px;
          overflow: hidden;
        }

        .home-head {
          min-height: 68px;
          display: flex;
          align-items: end;
          justify-content: space-between;
          gap: 24px;
          padding: 0 2px 10px;
          border-bottom: 1px solid var(--frl-border-strong);
        }

        .home-head p {
          margin: 0 0 5px;
          color: var(--frl-accent);
          font-size: 9px;
          font-weight: 850;
          letter-spacing: .15em;
          text-transform: uppercase;
        }

        .home-head h1 {
          margin: 0;
          font-size: clamp(25px, 3vw, 38px);
          line-height: .96;
          letter-spacing: -.055em;
        }

        .home-orient {
          display: flex;
          align-items: center;
          gap: 10px;
          padding-bottom: 2px;
          white-space: nowrap;
        }

        .home-orient span {
          padding: 5px 8px;
          background: rgba(154,170,66,.14);
          color: #687520;
          border-radius: 99px;
          font-size: 9px;
          font-weight: 850;
          letter-spacing: .08em;
          text-transform: uppercase;
        }

        .home-orient strong {
          color: var(--frl-muted);
          font-size: 10px;
          font-weight: 750;
        }

        .home-grid {
          min-height: 0;
          display: grid;
          grid-template-columns: minmax(0, 1.22fr) minmax(390px, .78fr);
          gap: 12px;
        }

        .home-primary,
        .home-h2h,
        .home-quick,
        .home-research {
          border: 1px solid var(--frl-border);
          text-decoration: none;
        }

        .home-primary {
          position: relative;
          min-height: 0;
          display: grid;
          grid-template-rows: auto minmax(0, 1fr) auto;
          overflow: hidden;
          padding: 22px;
          background: #1b1b18;
          color: #fffdf8;
          border-radius: 22px;
        }

        .home-card-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 12px;
        }

        .home-card-top small {
          color: #f18b72;
          font-size: 9px;
          font-weight: 850;
          letter-spacing: .13em;
          text-transform: uppercase;
        }

        .home-card-top span {
          color: rgba(255,253,248,.68);
          font-size: 10px;
          font-weight: 750;
        }

        .home-primary-core {
          min-height: 0;
          display: grid;
          grid-template-columns: minmax(0, 1fr) minmax(230px, .82fr);
          align-items: center;
          gap: 24px;
          padding: 14px 0;
        }

        .home-primary h2 {
          margin: 0;
          max-width: 560px;
          font-size: clamp(42px, 5vw, 68px);
          line-height: .88;
          letter-spacing: -.07em;
        }

        .home-primary h2 em {
          display: block;
          margin-top: 5px;
          color: #f18b72;
          font-family: Georgia, serif;
          font-weight: 500;
        }

        .home-primary-copy p {
          margin: 17px 0 0;
          color: rgba(255,253,248,.62);
          font-size: 11px;
          font-weight: 650;
          letter-spacing: .01em;
        }

        .mini-pitch {
          position: relative;
          width: min(100%, 330px);
          aspect-ratio: 1.42;
          justify-self: end;
          border: 1px solid rgba(255,253,248,.48);
          border-radius: 13px;
          background:
            linear-gradient(90deg, rgba(154,170,66,.15) 50%, rgba(154,170,66,.08) 50%),
            #31352a;
          box-shadow: 0 20px 42px rgba(0,0,0,.20);
        }

        .mini-pitch::before {
          content: "";
          position: absolute;
          left: 50%;
          top: 0;
          bottom: 0;
          border-left: 1px solid rgba(255,253,248,.42);
        }

        .mini-pitch::after {
          content: "";
          position: absolute;
          left: 50%;
          top: 50%;
          width: 24%;
          aspect-ratio: 1;
          border: 1px solid rgba(255,253,248,.42);
          border-radius: 50%;
          transform: translate(-50%, -50%);
        }

        .pitch-box {
          position: absolute;
          top: 24%;
          bottom: 24%;
          width: 16%;
          border: 1px solid rgba(255,253,248,.38);
        }

        .pitch-box.left { left: 0; border-left: 0; }
        .pitch-box.right { right: 0; border-right: 0; }

        .pitch-dot {
          position: absolute;
          width: 9px;
          height: 9px;
          border-radius: 50%;
          box-shadow: 0 0 0 4px rgba(255,255,255,.08);
        }

        .pitch-dot.a { left: 31%; top: 31%; background: #f18b72; }
        .pitch-dot.b { left: 40%; top: 65%; background: #f18b72; }
        .pitch-dot.c { right: 34%; top: 47%; background: #c4cf7b; }
        .pitch-dot.d { right: 20%; top: 70%; background: #c4cf7b; }

        .home-flow {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          border-top: 1px solid rgba(255,253,248,.13);
        }

        .home-flow span {
          position: relative;
          padding-top: 12px;
          color: rgba(255,253,248,.62);
          font-size: 9px;
          font-weight: 800;
          letter-spacing: .09em;
          text-transform: uppercase;
        }

        .home-flow span + span::before {
          content: "→";
          position: absolute;
          left: -15px;
          color: #f18b72;
        }

        .home-side {
          min-height: 0;
          display: grid;
          grid-template-rows: minmax(140px, .85fr) minmax(220px, 1.2fr) auto;
          gap: 10px;
        }

        .home-h2h {
          position: relative;
          min-height: 0;
          display: grid;
          align-content: end;
          overflow: hidden;
          padding: 18px;
          background: #f2ded7;
          border-radius: 17px;
        }

        .home-h2h::after {
          content: "VS";
          position: absolute;
          right: 15px;
          top: -18px;
          color: rgba(232,93,63,.13);
          font-size: 98px;
          font-weight: 900;
          letter-spacing: -.09em;
        }

        .home-h2h small,
        .home-quick small,
        .home-research small {
          font-size: 8px;
          font-weight: 850;
          letter-spacing: .12em;
          text-transform: uppercase;
        }

        .home-h2h small { color: #ad4933; }

        .home-h2h h2 {
          position: relative;
          z-index: 1;
          margin: 7px 0 4px;
          font-size: 27px;
          letter-spacing: -.05em;
        }

        .home-h2h p {
          position: relative;
          z-index: 1;
          margin: 0;
          color: #6f5d57;
          font-size: 10px;
          font-weight: 650;
        }

        .home-quick-grid {
          min-height: 0;
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          grid-template-rows: repeat(2, minmax(0, 1fr));
          gap: 8px;
        }

        .home-quick {
          min-height: 0;
          display: flex;
          flex-direction: column;
          justify-content: space-between;
          padding: 13px 14px;
          border-radius: 14px;
          transition: transform .15s ease, border-color .15s ease;
        }

        .home-quick:hover,
        .home-h2h:hover,
        .home-research:hover {
          transform: translateY(-2px);
          border-color: var(--frl-border-strong);
        }

        .home-quick[data-tone="olive"] { background: #e4e7c8; }
        .home-quick[data-tone="blue"] { background: #dce7e7; }
        .home-quick[data-tone="sand"] { background: #eee6d5; }
        .home-quick[data-tone="rose"] { background: #ead8d5; }

        .home-quick-top {
          display: flex;
          justify-content: space-between;
          color: var(--frl-muted);
          font-size: 8px;
          font-weight: 850;
        }

        .home-quick strong {
          display: block;
          margin-top: 7px;
          font-size: 20px;
          letter-spacing: -.04em;
        }

        .home-quick p {
          margin: 2px 0 0;
          color: var(--frl-muted);
          font-size: 9px;
          font-weight: 650;
        }

        .home-research {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 15px;
          min-height: 48px;
          padding: 10px 13px;
          background: #fffdf8;
          border-radius: 12px;
        }

        .home-research small { color: var(--frl-accent); }
        .home-research strong { font-size: 11px; }
        .home-research b { color: var(--frl-accent); font-size: 16px; }

        @media (max-width: 1120px) {
          .home-grid { grid-template-columns: minmax(0, 1.08fr) minmax(340px, .92fr); }
          .home-primary-core { grid-template-columns: minmax(0, 1fr) minmax(190px, .65fr); }
          .home-primary h2 { font-size: clamp(38px, 4.6vw, 57px); }
        }

        @media (max-width: 950px) {
          .home-workspace {
            height: auto;
            min-height: 0;
            overflow: visible;
          }
          .home-grid { grid-template-columns: 1fr; }
          .home-primary { min-height: 470px; }
          .home-side { grid-template-rows: auto; }
          .home-h2h { min-height: 155px; }
          .home-quick-grid { min-height: 300px; }
        }

        @media (max-width: 620px) {
          .home-head { align-items: flex-start; flex-direction: column; gap: 9px; }
          .home-orient strong { display: none; }
          .home-primary { min-height: 500px; padding: 17px; }
          .home-primary-core { grid-template-columns: 1fr; gap: 12px; }
          .mini-pitch { width: 75%; justify-self: start; }
          .home-primary h2 { font-size: 43px; }
          .home-flow span { font-size: 7px; }
          .home-flow span + span::before { left: -10px; }
          .home-quick-grid { grid-template-columns: 1fr 1fr; }
        }
      `}</style>

      <div className="home-workspace">
        <header className="home-head">
          <div>
            <p>Football Research Laboratory · Workspace</p>
            <h1>What do you want to investigate?</h1>
          </div>
          <div className="home-orient">
            <span>2026/27</span>
            <strong>Choose a workspace →</strong>
          </div>
        </header>

        <section className="home-grid" aria-label="FRL workspaces">
          <Link href="/matchday" className="home-primary">
            <div className="home-card-top">
              <small>Start here · Matchday</small>
              <span>Open workspace ↗</span>
            </div>

            <div className="home-primary-core">
              <div className="home-primary-copy">
                <h2>
                  One fixture.
                  <em>Everything around it.</em>
                </h2>
                <p>Form · model · team trends · player leaders · value checks</p>
              </div>

              <div className="mini-pitch" aria-hidden="true">
                <i className="pitch-box left" />
                <i className="pitch-box right" />
                <i className="pitch-dot a" />
                <i className="pitch-dot b" />
                <i className="pitch-dot c" />
                <i className="pitch-dot d" />
              </div>
            </div>

            <div className="home-flow" aria-label="FRL research flow">
              <span>State</span>
              <span>Evidence</span>
              <span>Prediction</span>
              <span>Test</span>
            </div>
          </Link>

          <div className="home-side">
            <Link href="/head-to-head" className="home-h2h">
              <small>Compare · Head to head</small>
              <h2>Two teams. Same lens.</h2>
              <p>Put the matchup evidence side by side.</p>
            </Link>

            <div className="home-quick-grid">
              {quickLinks.map((item) => (
                <Link
                  href={item.href}
                  className="home-quick"
                  data-tone={item.tone}
                  key={item.href}
                >
                  <div className="home-quick-top">
                    <span>{item.index}</span>
                    <span>↗</span>
                  </div>
                  <div>
                    <strong>{item.title}</strong>
                    <p>{item.note}</p>
                  </div>
                </Link>
              ))}
            </div>

            <Link href="/research" className="home-research">
              <div>
                <small>Research lab</small>
                <strong> Ask a broader football question</strong>
              </div>
              <b>→</b>
            </Link>
          </div>
        </section>
      </div>
    </AppShell>
  );
}
