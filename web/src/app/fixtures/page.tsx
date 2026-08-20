import { Suspense } from "react";
import { AppShell } from "@/components/AppShell";
import { FixtureExplorer } from "@/components/FixtureExplorer";

export default function FixturesPage() {
  return (
    <AppShell>
      <Suspense fallback={<div className="frl-empty-state">Loading fixtures…</div>}>
        <FixtureExplorer />
      </Suspense>
    </AppShell>
  );
}
