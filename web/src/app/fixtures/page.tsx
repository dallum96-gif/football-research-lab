import { Suspense } from "react";
import { AppShell } from "@/components/AppShell";
import { FixturesExperience } from "./FixturesExperience";

export default function FixturesPage() {
  return (
    <AppShell>
      <Suspense fallback={<div className="frl-empty-state">Loading fixtures…</div>}>
        <FixturesExperience />
      </Suspense>
    </AppShell>
  );
}
