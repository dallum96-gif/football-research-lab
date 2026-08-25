"""Relationship-aware registry for universal variable access.

The registry records *how* a variable is resolved without duplicating the
underlying source/query logic. Handlers are intentionally injected by the
existing FRL query/source layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Any

from variable_resolver import VariableDefinition, VariableResolver


@dataclass(frozen=True)
class VariableWiring:
    variable: VariableDefinition
    relationship: str
    handler_name: str


class VariableWiringRegistry:
    def __init__(self, definitions: Mapping[str, VariableDefinition] | None = None) -> None:
        self._definitions = dict(definitions or {})
        self._wiring: dict[str, VariableWiring] = {}
        self._handlers: dict[str, Callable[..., Any]] = {}

    def register(
        self,
        definition: VariableDefinition,
        *,
        relationship: str,
        handler_name: str,
        handler: Callable[..., Any] | None = None,
    ) -> None:
        self._definitions[definition.name] = definition
        self._wiring[definition.name] = VariableWiring(
            variable=definition,
            relationship=relationship,
            handler_name=handler_name,
        )
        if handler is not None:
            self._handlers[handler_name] = handler

    def wiring(self, name: str) -> VariableWiring:
        try:
            return self._wiring[name]
        except KeyError as exc:
            raise KeyError(f"No universal wiring registered for FRL variable: {name}") from exc

    def bind_handler(self, handler_name: str, handler: Callable[..., Any]) -> None:
        self._handlers[handler_name] = handler

    def resolver(self) -> VariableResolver:
        resolver = VariableResolver()
        for name, item in self._wiring.items():
            handler = self._handlers.get(item.handler_name)
            resolver.register(item.variable, handler)
        return resolver


__all__ = ["VariableWiring", "VariableWiringRegistry"]
