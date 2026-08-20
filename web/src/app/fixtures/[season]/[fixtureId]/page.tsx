type FixtureDetailProps = {
  params: Promise<{
    season: string;
    fixtureId: string;
  }>;
};

export default async function FixtureDetailPage({ params }: FixtureDetailProps) {
  const { season, fixtureId } = await params;

  return (
    <main className="frl-main">
      <div className="frl-eyebrow">Fixture</div>
      <h1 className="frl-title">Fixture Landing</h1>
      <div className="frl-context">
        Canonical fixture reference: {season} / {fixtureId}
      </div>
      <div className="frl-rule" />
      <section className="frl-panel">
        <div className="frl-panel-title">Next migration step</div>
        <p className="frl-panel-subtitle">
          This route is intentionally a placeholder. The fixture landing workspace will be built next from
          the same canonical fixture identity and Research Result contracts.
        </p>
      </section>
    </main>
  );
}
