from __future__ import annotations

import inspect
from collections.abc import Callable, Sequence
from typing import Any

from angela_voice_assistant.core import filtration
from angela_voice_assistant.core.exceptions import FilterAlreadyUsedError
from angela_voice_assistant.core.filtration import (
    Filter,
    TemplateUtteranceFilter,
)
from angela_voice_assistant.core.utterance import Utterance

__all__ = ("Handler", "Router",)


class Router:
    """Управляет обработчиками высказываний."""

    __slots__ = ("_filters", "_handlers", "_similarity_evaluator",)

    def __init__(self, *filters: Filter) -> None:
        self._filters = list(filters)
        self._handlers: list[Handler] = []

    def call_appropriate_handler(self, utterance: Utterance) -> None:
        if filtration.is_utterance_pass_filters(utterance, self._filters):
            for handler in self._handlers:
                called = handler.try_call(utterance)

                if called:
                    return True

        return False

    def on_utterance(
        self,
        *triggers: str | Utterance | Filter,
        make_utterances_parameterized: bool = False,
    ) -> Callable[..., Any]:
        def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
            self.lazily_add_handler(
                function,
                triggers,
                make_utterances_parameterized=make_utterances_parameterized
            )
            return function

        return decorator

    def lazily_add_handler(
        self,
        function: Callable[..., Any],
        triggers: Sequence[Filter | Utterance | str],
        make_utterances_parameterized: bool = False,
    ) -> None:
        filters = filtration.convert_into_filters(triggers)

        if make_utterances_parameterized:
            filtration.make_template_utterances_parameterized(filters)

        self.add_handler(Handler(function, filters))

    def add_handler(self, handler: Handler) -> None:
        for filter in handler.filters:
            if self.is_filter_used_anyone(filter):
                raise FilterAlreadyUsedError(filter)

        self._handlers.append(handler)

    def add_handlers(self, handlers: Sequence[Handler]) -> None:
        for handler in handlers:
            self.add_handler(handler)

    def include_router(self, router: Router) -> None:
        self.add_handlers(router.handlers)
        self.add_filters(router.filters)

    def include_routers(self, *routers: Router) -> None:
        for router in routers:
            self.include_router(router)

    def add_filter(self, filter: Filter) -> None:
        if self.is_filter_used_anyone(filter):
            raise FilterAlreadyUsedError(filter)

        self._filters.append(filter)

    def add_filters(self, filters: Sequence[Filter]) -> None:
        for filter in filters:
            self.add_filter(filter)
    
    def is_filter_used_anyone(self, filter: Filter) -> bool:
        return (
            self._is_filter_used_by_handlers(filter)
            or self._is_filter_used_by_handlers(filter)
        )

    def _is_filter_used_by_handlers(self, filter: Filter) -> bool:
        for handler in self._handlers:
            for handler_filter in handler.filters:
                if filter.is_equal(handler_filter):
                    return True

        return False

    def _is_filter_used_by_router(self, filter: Filter) -> bool:
        return any(
            filter.is_equal(router_filter) for router_filter in self._filters
        )

    @property
    def handlers(self) -> tuple[Handler, ...]:
        return tuple(self._handlers)

    @property
    def filters(self) -> tuple[Filter, ...]:
        return tuple(self._filters)


class Handler:
    __slots__ = ("_filters", "_function",)

    def __init__(
        self,
        function: Callable[..., Any],
        filters: list[Filter],
    ) -> None:
        self._function = function
        self._filters = filters

    def try_call(self, utterance: Utterance) -> bool:
        passed_parameters = {}
        expected_parameters = tuple(
            inspect.signature(self._function).parameters
        )

        for filter in self._filters:
            if filter.is_utterance_pass(utterance):
                if "utterance" in expected_parameters:
                    passed_parameters["utterance"] = utterance

                if (
                    isinstance(filter, TemplateUtteranceFilter)
                    and filter.template_utterance.parameterized
                ):
                    passed_parameters[expected_parameters[0]] = \
                        utterance.text[:len(filter.template_utterance)]

                self._function(**passed_parameters)
                return True

        return False

    def is_filter_used(self, filter: Filter) -> bool:
        return any(
            filter.is_equal(handler_filter) for handler_filter in self._filters
        )

    @property
    def filters(self) -> tuple[Filter, ...]:
        return tuple(self._filters)
