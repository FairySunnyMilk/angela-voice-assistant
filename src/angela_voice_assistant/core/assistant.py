from __future__ import annotations

import json
import random
import threading
from collections.abc import Callable
from queue import Empty, Queue
from threading import Thread
from typing import Any

import Levenshtein
import sounddevice
from vosk import KaldiRecognizer, Model

from angela_voice_assistant.config import config
from angela_voice_assistant.core.filtration import Filter
from angela_voice_assistant.core.routing import Router
from angela_voice_assistant.core.tts import TTS
from angela_voice_assistant.core.utterance import Utterance
from angela_voice_assistant.modules.local_llm import LocalLLM

__all__ = ("Dispatcher", "VoiceAssistant")


class VoiceAssistant(Router):
    """Предоставляет интерфейс для распознования и воспроизведения речи."""

    def __init__(self, tts: TTS, local_llm: LocalLLM, *filters: Filter) -> None:
        super().__init__(*filters)
        self._tts = tts
        self._local_llm = local_llm
        self._vosk_model = Model(config.VOSK_MODEL_PATH)
        self._utterances: Queue[Utterance] = Queue()
        self.q_llm: Queue[str] = Queue()

        self.server_utterance_handlers: list[threading.Thread] = []

        self.listening = threading.Event()
        self.listening.set()

        self.answers: dict[tuple[str, ...], tuple[str, ...]] | None = None

        self._is_working = True

    def recognize_speech(self) -> None:
        """Запускает цикл распознования речи, который добавляет распознанное
        выражение в очередь.
        """
        audio_queue: Queue[bytes] = Queue()
        recognizer = KaldiRecognizer(
            self._vosk_model,
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
            while self._is_working:
                self.listening.wait()

                try:
                    raw_data = audio_queue.get(timeout=0.1)
                except Empty:
                    continue

                if recognizer.AcceptWaveform(raw_data):
                    utterance_text = json.loads(
                        recognizer.Result()
                    ).get("text", "")
                    utterance = Utterance(utterance_text)

                    print("Распознанное выражение:", utterance.text)
                    self._utterances.put(utterance)

    def process_utterances(self) -> None:
        """Запускает цикл обработки распознанных высказваний."""
        while True:
            utterance = self._utterances.get()

            for filter in self._filters:
                if filter.is_utterance_pass(utterance):
                    handler_called  = self.call_appropriate_handler(utterance)

                    if not handler_called:
                        self.get_answer(utterance)
                    else:
                        self._tts.to_voice(random.choice(config.SPEED_ANSWER))

    def process_server_modules(self) -> None:
        """Start modules serve."""
        for mod_serv in self.server_utterance_handlers:
            mod_serv.start()
        for mod_serv in self.server_utterance_handlers:
            mod_serv.join()

    def get_text_llm(self, utterance: Utterance) -> None:
        text = utterance.text.casefold().strip()
        self.q_llm.put(text)
    
    def run_server(self) -> None:
        while self._is_working:
            try:
                text = self.q_llm.get(timeout=0.1)
            except Empty:
                continue
            self._tts.to_voice(self._local_llm.generate(prompt=text))

    def get_answer(self, utterance: Utterance) -> None:
        text = utterance.text.casefold().strip()

        if self.answers:
            for q, a in self.answers.items():
                if any(Levenshtein.distance(question, text) < 2 for question in q):
                    self._tts.to_voice(random.choice(a))
                    break

    def server_utterance(self) -> Callable[..., Any]:
        """Start server for your module"""
        def decorator(function: Callable[..., Any]) -> Callable[..., Any]:
            self.server_utterance_handlers.append(
                threading.Thread(target=function)
            )
            return function

        return decorator

    def set_answers(
        self, answers: dict[tuple[str, ...], tuple[str, ...]],
    ) -> None:
        """Устанавливает готовые ответы на высказывания.

        Args:
            answers: словарь, в котором ключ - высказывание, а значение -
                ответ на это высказывание."""
        self.answers = answers.copy()


class Dispatcher:
    __slots__ = (
        "_assistant",
        "_llm_thread",
        "_recognition_thread",
        "_utterance_proccessing_thread",
        "_utterance_server_thread",
    )

    def __init__(self, assistant: VoiceAssistant) -> None:
        self._recognition_thread = Thread(target=assistant.recognize_speech)
        self._utterance_proccessing_thread = Thread(target=assistant.process_utterances)
        self._utterance_server_thread = Thread(target=assistant.process_server_modules)
        self._llm_thread = Thread(target=assistant.run_server)

    def run(self) -> None:
        self._recognition_thread.start()
        self._utterance_proccessing_thread.start()
        self._utterance_server_thread.start()
        self._llm_thread.start()

        self._recognition_thread.join()
        self._utterance_proccessing_thread.join()
        self._utterance_server_thread.join()
        self._llm_thread.join()

    def stop(self) -> None:
        ...
