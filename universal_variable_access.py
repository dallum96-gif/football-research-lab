"""Public FRL variable-access facade.

Consumers call this facade with a canonical variable and football context.
Source-specific retrieval stays behind the registered relationship handlers.
"""
from __future__ import annotations

from typing import Any, Callable, Mapping

from variable_resolver import VariableDefinition, VariableResolver, register_variable
from variable_context import (
    FixtureContext,
    TeamFixtureContext,
    PlayerFixtureContext,
    PlayerSeasonContext,
    TeamSeasonContext,
    EventContext,
)


class UniversalVariableAccess:
    def __init__(self) -> None:
        self._resolver = VariableResolver()
        self._handlers: dict[str, Callable[..., Any]] = {}

    def register(
        self,
        definition: VariableDefinition,
        handler: Callable[..., Any],
    ) -> None:
        self._handlers[definition.name] = handler
        self._resolver.register(definition, handler)

    def resolve(self, variable: str, **context: Any) -> dict[str, Any]:
        return self._resolver.resolve(variable, **context).as_dict()

    def available(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))


_DEFAULT_ACCESS = UniversalVariableAccess()


def register_access_handler(
    definition: VariableDefinition,
    handler: Callable[..., Any],
) -> None:
    _DEFAULT_ACCESS.register(definition, handler)


def resolve_variable(variable: str, **context: Any) -> dict[str, Any]:
    return _DEFAULT_ACCESS.resolve(variable, **context)


def available_variables() -> tuple[str, ...]:
    return _DEFAULT_ACCESS.available()


__all__ = [
    "UniversalVariableAccess",
    "FixtureContext",
    "TeamFixtureContext",
    "PlayerFixtureContext",
    "PlayerSeasonContext",
    "TeamSeasonContext",
    "EventContext",
    "register_access_handler",
    "resolve_variable",
    "available_variables",
]
