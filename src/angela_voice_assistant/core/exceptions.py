from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from angela_voice_assistant.core.filtration import Filter
    from angela_voice_assistant.core.utterance import Utterance

__all__ = ("FilterAlreadyUsedError", "IndexingIntoEmptyUtteranceError")


class FilterAlreadyUsedError(Exception):
    __slots__ = ("_filter",)

    def __init__(self, filter: Filter) -> None:
        super().__init__()
        self._filter = filter

    def __str__(self) -> str:
        return f"Фильтр '{self._filter!r}' уже используется."


class IndexingIntoEmptyUtteranceError(Exception):
    __slots__ = ("_utterance", "_word_index")

    def __init__(self, utterance: Utterance, word_index: int) -> None:
        self._utterance = utterance
        self._word_index = word_index

    def __str__(self) -> str:
        return (
            f"Не возможно взять слово с индексом '{self._word_index}', так "
            f"как высказывание {self._utterance!r} пустое."
        )
