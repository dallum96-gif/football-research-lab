import { Suspense } from "react";
import { AppShell } from "@/components/AppShell";
import { FixtureExplorer } from "@/components/FixtureExplorer";
import { FixturesPremiumFrame } from "./FixturesPremiumFrame";

export default function FixturesPage() {
  return (
    <AppShell>
      <FixturesPremiumFrame>
        <Suspense fallback={<div className="frl-empty-state">Loading fixtures…</div>}>
          <FixtureExplorer />
        </Suspense>
      </FixturesPremiumFrame>
    </AppShell>
  );
}
