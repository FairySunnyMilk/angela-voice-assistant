import os
import queue
import json
import hashlib
import soundfile
import sounddevice
import Levenshtein

from typing import Callable
from vosk import Model, KaldiRecognizer
from silero_tts.silero_tts import SileroTTS

from angela_voice_assistant import config


class VoiceAssistant:
    # TODO: Add a docstring to the class.
    def __init__(self) -> None:
        self.vosk_model = Model(config.VOSK_MODEL_PATH)
        self.tts = SileroTTS(
            model_id="v5_ru",
            language="ru",
            speaker="baya",
            sample_rate=8000,
            device="cpu",
        )
        self.utterances: queue.Queue[str] = queue.Queue()
        self.utterance_handlers: dict[tuple[str], Callable] = {}

    def process_utterances(self) -> None:
        while True:
            utterance = self.utterances.get()

            if utterance:
                if self.is_assistant_called(utterance):
                    utterance = self.remove_key_phrase(utterance)
                    
                    self.try_invoke_appropriate_handler(utterance)
    
    def try_invoke_appropriate_handler(self, utterance: str) -> None:
        """Finds a suitable handler and calls it. If no suitable handler is 
        found, it does nothing.

        Args:
            utterance: The utterance for which a handler is being selected.
        """
        for trigger_utterances, utterance_handler in (
            self.utterance_handlers.items()
        ):
            for trigger_utterance in trigger_utterances:
                if Levenshtein.distance(utterance, trigger_utterance) < 2:
                    utterance_handler()
                    break

    def is_assistant_called(self, utterance: str) -> bool:
        """Checks whether the assistant is being addressed or not.

        Args:
            utterance: A utterance being checked for the presence of a form of address.
        
        Returns:
            Presence of a form of address in the utterance.
        """
        first_word = utterance.split()[0]

        return any(
            Levenshtein.distance(first_word, name_variation) <= 2
            for name_variation in config.VOICE_ASSISTANT_NAME_VARIATIONS
        )

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
            while True:
                raw_data = audio_queue.get()

                if recognizer.AcceptWaveform(raw_data):
                    utterance = json.loads(recognizer.Result()).get("text", "")
                    
                    print("Recognized speech:", utterance)  # TODO: refactor for logging
                    self.utterances.put(utterance)

    def speak(self, text: str) -> None:
        """Reads the text aloud.

        Args:
            text: Text for voiceover.
        """
        filename = self.generate_cached_speech_filename(text)

        if not os.path.exists(filename):
            self.tts.tts(text=text, output_file=filename)

        data, sample_rate = soundfile.read(filename)

        sounddevice.play(data, sample_rate)
        sounddevice.wait()

    def generate_cached_speech_filename(self, text: str) -> str:
        """Generates a hash-based filename for caching the speech.

        Args:
            text: Text for generating a hash for the filename.
        
        Returns:
            Hash-based filename for caching the speech.
        """
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        return os.path.join(config.CACHE_DIR, f"{text_hash}.wav")

    def on_utterance(self, *trigger_utterances: str) -> Callable:
        """Binds a function to the specified utterances so that the assistant 
        calls the function after hearing them.

        Args:
            trigger_utterances: The utterances that trigger the handler.
        
        Returns:
            A decorator that returns the function to which it is applied 
            without changes.
        
        Example:
            >>> assistant = VoiceAssistant()
            >>>
            >>> @assistant.on_utterance("what time is it", "tell me the time")
            ... def tell_time():
            ...     # Сode that will execute when the assistant 
            ...     # hears the specified utterances.
            ...     pass
        """
        def decorator(function: Callable) -> Callable:
            self.utterance_handlers[trigger_utterances] = function
            return function

        return decorator
