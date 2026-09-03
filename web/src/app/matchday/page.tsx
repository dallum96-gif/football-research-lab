import { redirect } from "next/navigation";
import { AppShell } from "@/components/AppShell";

const API_BASE = (process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
const DEFAULT_SEASON = "2026-27";

type FixtureOption = {
  fixture_id: string;
  kickoff_time: string | null;
  completed: boolean;
};

type FixturePayload = {
  fixtures: FixtureOption[];
};

export const dynamic = "force-dynamic";

export default async function MatchdayPage() {
  let payload: FixturePayload | null = null;

  try {
    const response = await fetch(`${API_BASE}/api/v1/matchday/fixtures/${DEFAULT_SEASON}`, {
      cache: "no-store",
    });
    if (response.ok) payload = await response.json() as FixturePayload;
  } catch {
    payload = null;
  }

  if (!payload?.fixtures.length) {
    return (
      <AppShell>
        <div className="frl-empty-state">
          <strong>Matchday Stat Pack unavailable.</strong>
          <span>Start the FRL API and reload this page.</span>
        </div>
      </AppShell>
    );
  }

  const now = Date.now();
  const ordered = [...payload.fixtures].sort((a, b) =>
    String(a.kickoff_time ?? "").localeCompare(String(b.kickoff_time ?? "")),
  );
  const next = ordered.find((fixture) => {
    if (fixture.completed || !fixture.kickoff_time) return false;
    const kickoff = new Date(fixture.kickoff_time).getTime();
    return Number.isFinite(kickoff) && kickoff >= now;
  }) ?? ordered.find((fixture) => !fixture.completed) ?? ordered.at(-1);

  if (next) redirect(`/matchday/${DEFAULT_SEASON}/${next.fixture_id}`);

  return null;
}
