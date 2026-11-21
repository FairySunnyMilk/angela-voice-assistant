from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from types import NotImplementedType
from typing import override

import Levenshtein

from angela_voice_assistant.core.exceptions import (
    IndexingIntoEmptyUtteranceError,
)
from angela_voice_assistant.core.utterance import Utterance

__all__ = (
    "AssistantAddressFilter",
    "Filter",
    "LevenshteinSimilarityEvaluator",
    "NotEmptyFilter",
    "SimilarityEvaluator",
    "TemplateUtteranceFilter",
    "is_utterance_pass_filters",
    "make_template_utterances_parameterized",
)


class Filter(ABC):
    @abstractmethod
    def is_utterance_pass(self, utterance: Utterance) -> bool: ...

    def is_equal(self, filter: Filter) -> bool:
        return isinstance(filter, self.__class__)

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if isinstance(other, Filter):
            return self.is_equal(other)

        return NotImplemented

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class TemplateUtteranceFilter(Filter):
    __slots__ = ("_similarity_evaluator", "_template_utterance",)

    def __init__(
        self,
        template_utterance: str | Utterance,
        similarity_evaluator: SimilarityEvaluator,
    ) -> None:
        if isinstance(template_utterance, str):
            template_utterance = Utterance(template_utterance)
        
        self._template_utterance = template_utterance
        self._similarity_evaluator = similarity_evaluator

    @override
    def is_utterance_pass(self, utterance: Utterance) -> bool:
        if utterance.parameterized:
            return self._similarity_evaluator.startswith(
                utterance.text,
                self._template_utterance.text
            )

        return self._similarity_evaluator.is_similar(
            utterance.text,
            self._template_utterance.text
        )

    @override
    def is_equal(self, filter: Filter) -> bool:
        if isinstance(filter, TemplateUtteranceFilter):
            return filter.template_utterance == self.template_utterance

        return False

    @property
    def template_utterance(self) -> Utterance:
        return self._template_utterance

    @template_utterance.setter
    def template_utterance(self, utterance: Utterance) -> None:
        self._template_utterance = utterance

    @override
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(template_utterance='{self.template_utterance!r}')"
        )


class AssistantAddressFilter(Filter):
    __slots__ = ("_assistant_name_variation",)

    _FIRST_WORD_INDEX = 0

    def __init__(self, assistant_name_variation: tuple[str, ...]) -> None:
        self._assistant_name_variation = assistant_name_variation

    @override
    def is_utterance_pass(self, utterance: Utterance) -> bool:
        return self._contain_call_to_assistant(utterance)

    def _contain_call_to_assistant(self, utterance: Utterance) -> bool:
        try:
            return (
                utterance.get_word_by_index(self._FIRST_WORD_INDEX)
                in self._assistant_name_variation
            )
        except IndexingIntoEmptyUtteranceError, IndexError:
            return False


class NotEmptyFilter(Filter):
    @override
    def is_utterance_pass(self, utterance: Utterance) -> bool:
        return bool(utterance.text)


class SimilarityEvaluator(ABC):
    @abstractmethod
    def is_similar(self, expression1: str, expression2: str) -> bool: ...

    @abstractmethod
    def startswith(self, expression: str, prefix: str) -> bool: ...


class LevenshteinSimilarityEvaluator(SimilarityEvaluator):
    @override
    def is_similar(self, expression1: str, expression2: str) -> bool:
        return Levenshtein.distance(expression1, expression2) / max(
            len(expression1), len(expression2)
        ) < 0.5  # TODO: Выделить в конфиг.

    @override
    def startswith(self, expression: str, prefix: str) -> bool:
        return self.is_similar(expression[:len(prefix)], prefix)


def is_utterance_pass_filters(
    utterance: Utterance,
    filters: Sequence[Filter],
) -> bool:
    return any(filter.is_utterance_pass(utterance) for filter in filters)


def make_template_utterances_parameterized(filters: Sequence[Filter]) -> None:
    for filter in filters:
        if isinstance(filter, TemplateUtteranceFilter):
            filter.template_utterance = \
                filter.template_utterance.to_parameterized()


def convert_into_filters(
    triggers: Sequence[str | Utterance | Filter],
) -> list[Filter]:
    filters: list[Filter] = []

    for trigger in triggers:
        if isinstance(trigger, str | Utterance):
            filters.append(TemplateUtteranceFilter(
                trigger,
                LevenshteinSimilarityEvaluator()
            ))
        else:
            filters.append(trigger)

    return filters
