# Universal Variable Access — Implementation Note

PR #27 establishes the first universal variable-access seam on `feature/universal-variable-access`.

The first slice intentionally does not invent a new player-match source join. It establishes:

- the durable universal variable-access contract;
- a source-agnostic resolver API;
- initial metadata definitions for the six agreed fixture-page player variables;
- fail-closed resolver tests.

The next implementation step is to register the existing, validated source/query handlers at the resolver seam so requests return real player-fixture values. This must reuse the existing identity/retrieval mechanisms rather than creating parallel joins.
