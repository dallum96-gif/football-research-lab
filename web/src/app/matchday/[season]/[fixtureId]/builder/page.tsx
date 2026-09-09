import { notFound } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { MatchdayBetBuilderReference } from "./MatchdayBetBuilderReference";

const API_BASE = (process.env.NEXT_PUBLIC_FRL_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

type MatchdayBuilderPageProps = {
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

export default async function MatchdayBuilderPage({ params }: MatchdayBuilderPageProps) {
  const { season, fixtureId } = await params;
  const encodedSeason = encodeURIComponent(season);
  const encodedFixture = encodeURIComponent(fixtureId);
  const [pack, marketPack] = await Promise.all([
    getJson<Record<string, unknown>>(`/api/v1/matchday/${encodedSeason}/${encodedFixture}`),
    getJson<Record<string, unknown>>(`/api/v1/head-to-head/${encodedSeason}/${encodedFixture}`),
  ]);

  if (!pack) notFound();

  return (
    <AppShell>
      <MatchdayBetBuilderReference
        key={`${season}-${fixtureId}`}
        pack={pack}
        marketPack={marketPack}
      />
    </AppShell>
  );
}
