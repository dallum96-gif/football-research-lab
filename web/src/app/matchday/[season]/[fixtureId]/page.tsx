import Link from "next/link";
import { notFound } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { MatchdayWorkspaceV2 } from "./MatchdayWorkspaceV2";
import "./MatchdayColour.css";

const API_BASE = (process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

type MatchdayPageProps = {
  params: Promise<{ season: string; fixtureId: string }>;
};

export const dynamic = "force-dynamic";

async function getJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (response.status === 404) return null;
    if (!response.ok) throw new Error(`FRL API request failed: ${response.status}`);
    return await response.json() as T;
  } catch {
    return null;
  }
}

export default async function MatchdayFixturePage({ params }: MatchdayPageProps) {
  const { season, fixtureId } = await params;
  const [pack, fixtures] = await Promise.all([
    getJson<Record<string, unknown>>(`/api/v1/matchday/${encodeURIComponent(season)}/${encodeURIComponent(fixtureId)}`),
    getJson<{ fixtures: Array<Record<string, unknown>> }>(`/api/v1/matchday/fixtures/${encodeURIComponent(season)}`),
  ]);

  if (!pack) notFound();

  return (
    <AppShell>
      <div className="frl-matchday-colour">
        <div style={{ display: "flex", justifyContent: "flex-end", margin: "0 0 .65rem" }}>
          <Link
            href={`/head-to-head/${encodeURIComponent(season)}/${encodeURIComponent(fixtureId)}`}
            style={{
              display: "inline-flex",
              alignItems: "center",
              minHeight: "2.2rem",
              padding: "0 .8rem",
              borderRadius: "999px",
              background: "var(--frl-text)",
              color: "var(--frl-bg)",
              textDecoration: "none",
              fontSize: ".72rem",
              fontWeight: 800,
            }}
          >
            Head-to-Head + BetBuilder Pack →
          </Link>
        </div>
        <MatchdayWorkspaceV2
          pack={pack}
          fixtureOptions={fixtures?.fixtures ?? []}
        />
      </div>
    </AppShell>
  );
}
