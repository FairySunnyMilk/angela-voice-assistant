from __future__ import annotations

import hashlib
import inspect
import json
import os
import queue
import threading
from collections.abc import Callable
from typing import Any

import Levenshtein
import sounddevice
import soundfile
from silero_tts.silero_tts import SileroTTS
from vosk import KaldiRecognizer, Model

from angela_voice_assistant import config


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
        self.utterances: queue.Queue[Utterance] = queue.Queue()
        self.utterance_handlers: list[UtteranceHandler] = []
        self.default_utterance_handler: UtteranceHandler | None = None

        self.listening = threading.Event()
        self.listening.set()

        self.processing_utterances = threading.Event()
        self.processing_utterances.set()

    def recognize_speech(self) -> None:
        """Starts a speech recognition loop that adds the recognized speech 
        text to the queue.
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
            while self.listening.is_set():
                try:
                    raw_data = audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                if recognizer.AcceptWaveform(raw_data):
                    utterance_text = json.loads(recognizer.Result()).get("text", "")
                    utterance = Utterance(utterance_text)
                    
                    print("Recognized speech:", utterance.text)  # TODO: refactor for logging
                    self.utterances.put(utterance)

    def process_utterances(self) -> None:
        """Starts a loop that processes utterances received from the user.
        """
        while self.processing_utterances.is_set():
            utterance = self.utterances.get()

            if utterance.text and utterance.contain_call_to_assistant():
                utterance.remove_call_to_assistant()

                self.call_appropriate_handler(utterance)

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
                    return

        if self.default_utterance_handler:
            self.default_utterance_handler({"text": text})

    def speak(self, text: str) -> None:
        """Reads the text aloud.

        Args:
            text: Text for voiceover.
        """
        self.listening.clear()

        filename = self.generate_cached_speech_filename(text)

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
            speech_text: Text for generating a hash for the filename.
        
        Returns:
            Hash-based filename for caching the speech.
        """
        text_hash = hashlib.md5(speech_text.encode("utf-8")).hexdigest()
        return os.path.join(config.CACHE_DIR, f"{text_hash}.wav")

    def on_utterance(self, *trigger_utterances: str) -> Callable[..., Any]:
        """Binds a function to the specified utterances so that the assistant 
        calls it then whey are heard.

        Args:
            trigger_utterances: Utterances that trigger the function. If
                trigger_utterances is empty, the function will trigger on any
                non-empty utterance.        

        Returns:
            Callable[..., Any]: A decorator that registers the function and 
                returns it unchanged.
        
        Example:
            >>> assistant = VoiceAssistant()
            >>>
            >>> @assistant.on_utterance("what time is it", "tell me the time")
            ... def tell_time():
            ...     # Code that will execute when the assistant 
            ...     # hears the specified utterances.
            ...     pass
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


class Utterance:
    def __init__(self, text: str) -> None:
        self._text = text

    def contain_call_to_assistant(self) -> bool:
        first_word = self._text.split(maxsplit=2)[0]

        return any(
            Levenshtein.distance(first_word, name_variation) <= 2
            for name_variation in config.VOICE_ASSISTANT_NAME_VARIATIONS
		)
	
    def remove_call_to_assistant(self) -> None:
        if self.contain_call_to_assistant():
            self._text = self._text.split(maxsplit=1)[-1] if len(self._text.split()) > 1 else ""
        else:
            raise ValueError(
                "The utterance does not contain a call to the assistant."
            )

    @property
    def text(self) -> str:
        return self._text


class UtteranceHandler:
    def __init__(
        self,
        endpoint: Callable[..., Any],
		trigger_utterances: tuple[Utterance, ...],
    ) -> None:
        self._endpoint = endpoint
        self._trigger_utterances = trigger_utterances
        self._params_names = list(inspect.signature(endpoint).parameters)

    def __call__(self, params: dict[str, str] | None = None) -> None:
        self._endpoint(**(params or {}))
