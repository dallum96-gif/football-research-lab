"""Enforcement helpers for FRL relationship contracts.

This module is deliberately thin: it does not discover identities and does not
perform fuzzy joins. It validates an already-produced relationship candidate
against the shared relationship contract before downstream code may promote it.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from relationship_contracts import EvidenceClass, get_relationship_contract


@dataclass(frozen=True)
class RelationshipDecision:
    contract: str
    status: EvidenceClass
    candidate_count: int
    source_context_available: bool
    contradiction: bool = False
    reason: str = ""

    @property
    def verified(self) -> bool:
        return self.status == "VERIFIED"


def evaluate_identity(
    contract_name: str,
    *,
    source_context_available: bool,
    candidates: list[Mapping] | tuple[Mapping, ...],
    contradiction: bool = False,
) -> RelationshipDecision:
    """Evaluate a candidate identity without promoting uncertain evidence."""
    contract = get_relationship_contract(contract_name)
    if contract.kind != "IDENTITY":
        raise ValueError(f"{contract_name} is not an IDENTITY contract")

    candidate_count = len(candidates)
    if contradiction:
        status: EvidenceClass = "CONTRADICTORY"
        reason = "Contradictory evidence detected."
    elif not source_context_available:
        status = "UNAVAILABLE"
        reason = contract.absent_means
    elif candidate_count == 0:
        status = "UNRESOLVED"
        reason = "No deterministic candidate satisfied the relationship evidence."
    elif candidate_count == 1:
        status = "VERIFIED"
        reason = "Exactly one deterministic candidate satisfied the relationship evidence."
    else:
        status = "AMBIGUOUS"
        reason = "Multiple deterministic candidates remain."

    return RelationshipDecision(
        contract=contract_name,
        status=status,
        candidate_count=candidate_count,
        source_context_available=source_context_available,
        contradiction=contradiction,
        reason=reason,
    )


def require_verified(decision: RelationshipDecision) -> None:
    """Fail closed when a downstream path requires a verified relationship."""
    if not decision.verified:
        raise ValueError(
            f"Relationship contract '{decision.contract}' is not verified: "
            f"{decision.status}. {decision.reason}"
        )


def classify_observation(*, identity_verified: bool, fixture_verified: bool, observation_present: bool) -> EvidenceClass:
    """Classify an observation without treating absence as identity failure."""
    get_relationship_contract("player_identity_to_player_match_observations")
    if identity_verified and fixture_verified and observation_present:
        return "VERIFIED"
    if not identity_verified or not fixture_verified:
        return "UNAVAILABLE"
    return "UNAVAILABLE"


def field_available(field: str, season_fields: tuple[str, ...] | list[str] | set[str]) -> bool:
    """Check source-field availability without manufacturing values."""
    get_relationship_contract("source_field_to_season_availability")
    return field in set(season_fields)


def decision_dict(decision: RelationshipDecision) -> dict[str, object]:
    return {
        "relationship_contract": decision.contract,
        "relationship_status": decision.status,
        # Backward-compatible alias for existing diagnostics.
        "identity_status": decision.status,
        "candidate_count": decision.candidate_count,
        "source_context_available": decision.source_context_available,
        "contradiction": decision.contradiction,
        "verified": decision.verified,
        "reason": decision.reason,
    }
