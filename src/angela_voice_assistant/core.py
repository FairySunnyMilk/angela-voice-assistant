"""Представляет ядро ассистента.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import os
import queue
import threading
import random
from collections.abc import Callable
from typing import Any

import Levenshtein
import sounddevice
import soundfile
from silero_tts.silero_tts import SileroTTS
from vosk import KaldiRecognizer, Model

from angela_voice_assistant import config
from angela_voice_assistant.logging import logging

LOG = logging(path='log')


LOG.log_class()
class VoiceAssistant:
    def __init__(self) -> None:
        self.vosk_model = Model(config.VOSK_MODEL_PATH)

        self.tts = SileroTTS(
            model_id="v5_ru",
            language="ru",
            speaker="baya",
            sample_rate=8000,
            device="cpu",
        )

        self.q_llm: queue.Queue = queue.Queue()
        self.utterances: queue.Queue[Utterance] = queue.Queue()
        self.utterance_handlers: list[UtteranceHandler] = []
        self.default_utterance_handler: UtteranceHandler | None = None
        self.server_utterance_handlers: list[threading.Thread] = []

        self.listening = threading.Event()
        self.listening.set()

        self.default_answer: dict[tuple[str], tuple[str]] = {}

        if not os.path.exists(config.CACHE_DIR):
            os.mkdir(config.CACHE_DIR)

        super().__init__(model_name=config.NAME_LLM_MODEL)

    def recognize_speech(self) -> None:
        """Запускает цикл распознования речи, который добавляет распознанное
        выражение в очередь.
        """
        audio_queue = queue.Queue()
        recognizer = KaldiRecognizer(
            self.vosk_model,
            config.VOSK_SAMPLE_RATE,
        )

        def audio_callback(indata, frames, time, status):
            if status:
                print(status)
            audio_queue.put(bytes(indata))

        with sounddevice.RawInputStream(
            device=config.VOSK_MICROPHONE_NUMBER,
            samplerate=config.VOSK_SAMPLE_RATE,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=audio_callback,
        ):
            while self.IS_WORKING_ASSISTENT:
                self.listening.wait()

                try:
                    raw_data = audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                if recognizer.AcceptWaveform(raw_data):
                    utterance_text = json.loads(recognizer.Result()).get("text", "")
                    utterance = Utterance(utterance_text)
                    
                    print("Распознанное выражение:", utterance.text)  # TODO: refactor for logging
                    self.utterances.put(utterance)

    def process_utterances(self) -> None:
        """Запускает цикл обработки распознанных высказваний.
        """
        while self.IS_WORKING_ASSISTENT:
            utterance = self.utterances.get()

            if utterance.text and utterance.contain_call_to_assistant():
                utterance.remove_call_to_assistant()

                if utterance.text:
                    if self.call_appropriate_handler(utterance): ...
                    elif self.get_answer(utterance): ...
                    else: self.get_text_llm(utterance)
                else:
                    self.speak(random.choice(
                        config.SPEED_ANSWER
                    ))

    def process_server_modules(self) -> None:
        """
        Start modules server.
        """
        for mod_serv in self.server_utterance_handlers:
            mod_serv.start()
        for mod_serv in self.server_utterance_handlers:
            mod_serv.join()

    def call_appropriate_handler(self, utterance: Utterance) -> None:
        text = utterance.text.casefold().strip()

        for handler in self.utterance_handlers:
            for trigger in handler._trigger_utterances:
                phrase = trigger.text.casefold().strip()

                if text == phrase or text.startswith(phrase + " "):
                    argument = text[len(phrase):].strip()
                    params = {}

                    if handler._params_names:
                        params[handler._params_names[0]] = argument

                    handler(params)
                    return True

        if self.default_utterance_handler:
            self.default_utterance_handler({"text": text})
        return False

    def get_answer(self, utterance: Utterance) -> bool:
        text = utterance.text.casefold().strip()

        for q, a in self.default_answer.items():
            if any([
                Levenshtein.distance(question, text) < 2 for question in q
            ]):
                self.speak(random.choice(a))
                break



    def speak(self, text: str) -> None:
        """Воспроизводит переданный текст.

        Args:
            text: Текст для воспроизведения.
        """
        self.listening.clear()

        filename = self.get_cached_speech_filename(text)

        if not os.path.exists(filename):
            self.tts.tts(text=text, output_file=filename)

        data, sample_rate = soundfile.read(filename)

        sounddevice.play(data, sample_rate)
        sounddevice.wait()

        self.listening.set()

    @staticmethod
    def generate_cached_speech_filename(speech_text: str) -> str:
        """Generates a hash-based filename for caching the speech.

        Args:
            speech_text: Текст речи, на основе котрого создаётся хеш.
        
        Returns:
            Хеш-имя файла. Если файл речи с переданным текстом уже существует,
            то вернёт его имя.
        """
        text_hash = hashlib.md5(speech_text.encode("utf-8")).hexdigest()
        return os.path.join(config.CACHE_DIR, f"{text_hash}.wav")

    def server_utterance(self):
        """
        Start server for your modul
        """
        def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
            self.server_utterance_handlers.append(threading.Thread(target=function))
            return function
        return decorator

    def on_utterance(
        self,
        *trigger_utterances: str | None,
    ) -> Callable[..., Any]:
        """Привязывает функцию к `trigger_utterances`. После того, как
        ассистент распознаст выражение, схожее с любым выражением из
        `trigger_utterances`, вызовется эта фкнкция.

        Если эта же функция принимает аргумент, то в него передастся остаток
        распознанной речи.

        Args:
            trigger_utterances: Выражения, на которые будет срабатывать
                функция. Если параметр пуст (является `None`), то функция
                будет срабатывать на любое непоустое высказвание.

        Returns:
            Callable[..., Any]: Декоратор, регистрирующий функцию, оставляя
                её без изменений.
        
        Examples:
            Создание экземпляра:
            >>> assistant = VoiceAssistant()

            Регистрация обработчика:
            >>> @assistant.on_utterance("what time is it", "tell me the time")
            ... def tell_time():
            ...     # Запустится когда ассистент распознаст
            ...     # указанные выражения.
            ...     pass

            Использование параметров:
            >>> @assistant.on_utterance("найди в интернете")
            ... def search_on_internet(query):
            ...     # Если указан параметр, то в него передастся остаток
            ...     # распознанного выражения.
            ...     pass
            
            Обработчик по умолчанию:
            >>> @assistant.on_utterance()
            ... def reply_with_llm():
            ...     # Запустится когда ассистент распознаст любое 
            ...     # не пустое высказывание.
        """
        trigger_utterances = tuple(map(Utterance, trigger_utterances))
        
        def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
            handler = UtteranceHandler(function, trigger_utterances)
            
            if trigger_utterances:
                self.utterance_handlers.append(handler)
            else:
                 self.default_utterance_handler = handler
                
            return function

        return decorator

    def set_answers(
        self, answers: dict[tuple[str], tuple[str]],
    ) -> None:
        """Устанавливает готовые ответы на высказывания.

        Args:
            answers: словарь, в котором ключ - высказывание, а значение -
                ответ на это высказывание."""
        self.answers = answers.copy()


class Utterance:
    """Предоставляет интерфейс для работы с высказыванием пользователя.

    Example:
        >>> utterance = Utterance("Анжела, расскажи о себе")
        >>>
        >>> # Проверяем, есть ли обращение
        >>> utterance.contain_call_to_assistant()
        True
        >>>
        >>> # Удаляем обращение
        >>> utterance.remove_call_to_assistant()
        >>>
        >>> # Снова проверяем
        >>> utterance.contain_call_to_assistant()
        False
    """
    def __init__(self, text: str) -> None:
        """
        Args:
            text: Текст высказывания.
        """
        self._text = text

    def contain_call_to_assistant(self) -> bool:
        """Проверяет, содержится ли в `Utterance` обращение к ассистенту. Для
        этого смотрит на то, является ли первое слово вариацией имени
        ассистента.

        Returns:
            Наличие обращения.
        """
        first_word = self._text.split(maxsplit=2)[0]

        return any(
            Levenshtein.distance(first_word, name_variation) <= 2
            for name_variation in config.VOICE_ASSISTANT_NAME_VARIATIONS
        )
    
    def remove_call_to_assistant(self) -> None:
        """Если в `Utterance` есть обращение к ассистенту, то удаляет его.
        """
        if self.contain_call_to_assistant():
            self._text = self._text.split(maxsplit=1)[-1] if len(self._text.split()) > 1 else ""
        else:
            raise ValueError(
                "В Utterance нет обращения к ассистенту.."
            )

    @property
    def text(self) -> str:
        return self._text


class UtteranceHandler:
    """Предоставляет интерфейс для работы с обработчиком высказвания
    пользователя.  

    Example:
        >>> def some_function():
        ...     # Функция для примера.
        ...     pass
        ...
        >>> handler = UtteranceHandler(
        ...     some_function,
        ...     (
        ...         Utterance("Анжела, подскажи время"),
        ...     )
        ... )
        >>>
        >>> # Вызывает some_function()
        >>> handler()
    """
    def __init__(
        self,
        endpoint: Callable[..., Any],
        trigger_utterances: tuple[Utterance, ...],
    ) -> None:
        """
        Args:
            endpoint: Обработчик (функция), который будет срабатывать при
                вызове `UtteranceHandler`.
            trigger_utterances: Выражения, на которые должен срабатывать
                обработчик.
        """
        self._endpoint = endpoint
        self._trigger_utterances = trigger_utterances
        self._params_names = list(inspect.signature(endpoint).parameters)

    def __call__(self, params: dict[str, str] | None = None) -> None:
        self._endpoint(**(params or {}))
