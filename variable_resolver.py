"""Universal FRL variable resolution seam.

This module is intentionally thin: variable metadata determines the supported
resolution family, while existing query/source mechanisms remain responsible
for identity, provenance and source-specific retrieval.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping


class VariableResolutionError(ValueError):
    """Base error for safe, fail-closed variable resolution."""


class UnknownVariableError(VariableResolutionError):
    pass


class UnvalidatedVariableError(VariableResolutionError):
    pass


class UnsupportedContextError(VariableResolutionError):
    pass


@dataclass(frozen=True)
class VariableDefinition:
    name: str
    label: str
    grain: str
    status: str
    resolver: str | None = None
    definition: str | None = None
    source_family: str | None = None
    source_field: str | None = None
    value_type: str | None = None
    unit: str | None = None
    coverage: str | None = None
    derived_from: tuple[str, ...] = ()


@dataclass(frozen=True)
class VariableResult:
    variable: VariableDefinition
    context: Mapping[str, Any]
    values: Any
    status: str = "RESOLVED"

    def as_dict(self) -> dict[str, Any]:
        return {
            "variable": self.variable.name,
            "label": self.variable.label,
            "grain": self.variable.grain,
            "status": self.status,
            "context": dict(self.context),
            "values": self.values,
            "source": {
                "family": self.variable.source_family,
                "field": self.variable.source_field,
                "coverage": self.variable.coverage,
            },
            "definition": self.variable.definition,
            "transformation": {
                "derived_from": list(self.variable.derived_from),
            },
        }


class VariableResolver:
    """Resolve validated FRL variables through registered retrieval seams.

    The resolver deliberately does not contain source-specific joins. Those
    belong in the existing query/retrieval layer and are registered here by a
    small callable so that GUI consumers remain source-agnostic.
    """

    def __init__(
        self,
        definitions: Mapping[str, VariableDefinition] | None = None,
        handlers: Mapping[str, Callable[..., Any]] | None = None,
    ) -> None:
        self._definitions = dict(definitions or {})
        self._handlers = dict(handlers or {})

    def register(
        self,
        definition: VariableDefinition,
        handler: Callable[..., Any] | None = None,
    ) -> None:
        self._definitions[definition.name] = definition
        if handler is not None:
            self._handlers[definition.name] = handler

    def definition(self, name: str) -> VariableDefinition:
        try:
            return self._definitions[name]
        except KeyError as exc:
            raise UnknownVariableError(
                f"Unknown FRL variable: {name}"
            ) from exc

    def resolve(self, name: str, **context: Any) -> VariableResult:
        definition = self.definition(name)

        if definition.status not in {"VALIDATED", "RESOLVABLE", "GUI_ACCESSIBLE"}:
            raise UnvalidatedVariableError(
                f"FRL variable '{name}' is not validated for consumer access "
                f"(status={definition.status})."
            )

        if definition.resolver is None or name not in self._handlers:
            raise UnsupportedContextError(
                f"FRL variable '{name}' is catalogued but has no registered "
                "resolution handler for this consumer path."
            )

        values = self._handlers[name](**context)
        return VariableResult(
            variable=definition,
            context=context,
            values=values,
        )


_DEFAULT_RESOLVER = VariableResolver()


def register_variable(
    definition: VariableDefinition,
    handler: Callable[..., Any] | None = None,
) -> None:
    _DEFAULT_RESOLVER.register(definition, handler)


def resolve_variable(name: str, **context: Any) -> dict[str, Any]:
    """Resolve a canonical FRL variable into a serialisable result object."""
    return _DEFAULT_RESOLVER.resolve(name, **context).as_dict()


def variable_definition(name: str) -> VariableDefinition:
    return _DEFAULT_RESOLVER.definition(name)
