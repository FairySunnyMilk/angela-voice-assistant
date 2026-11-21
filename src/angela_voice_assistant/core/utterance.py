from dataclasses import dataclass

import Levenshtein

from angela_voice_assistant.core.exceptions import (
    IndexingIntoEmptyUtteranceError,
)

__all__ = ("Utterance",)


@dataclass(frozen=True, slots=True)
class Utterance:
    """Высказывание пользователя."""

    text: str
    parameterized: bool = False

    def is_empty(self) -> bool:
        """Проверяет, пустое ли высказывание.

        Returns:
            Пустое ли высказывание.
        """
        return not bool(self.text)

    def get_word_by_index(self, index: int) -> str:
        splitted_text = self.text.split()

        if not splitted_text:
            raise IndexingIntoEmptyUtteranceError(self, index)

        return splitted_text[index]

    def remove_word_by_index(self, index: int) -> Utterance:
        splitted_text = self.text.split()

        if not splitted_text:
            raise IndexingIntoEmptyUtteranceError(self, index)

        del splitted_text[index]

        return Utterance("".join(splitted_text))

    def match(self, utterance: Utterance) -> bool:
        return Levenshtein.distance(self.text, utterance.text) <= 2

    def to_parameterized(self) -> Utterance:
        return Utterance(self.text, parameterized=True)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(text='{self.text}', "
            f"parameterized={self.parameterized})"
        )

    def __len__(self) -> int:
        return len(self.text)
