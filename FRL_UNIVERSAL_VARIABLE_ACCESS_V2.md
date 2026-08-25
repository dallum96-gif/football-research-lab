# FRL Universal Variable Access V2

The consumer contract is deliberately broader than the curated GUI catalogue.

A source-native variable may be requested by its field name when the requested season empirically contains that field in a supported source family. The resolver remains source-agnostic and delegates retrieval to the existing research-field query layer.

This creates two complementary access modes:

1. **Canonical aliases / derived variables** for stable FRL concepts such as `passCompletionPct`.
2. **Native source variables** for the broader source universe, discovered from the requested season and returned with source-family/field provenance.

The UI may choose which variables to prominently display; accessibility is a separate concern from presentation.
