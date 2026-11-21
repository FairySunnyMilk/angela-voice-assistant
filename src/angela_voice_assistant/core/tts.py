import os
import threading

import sounddevice
import soundfile
from silero_tts.silero_tts import SileroTTS

from angela_voice_assistant.core import utils

__all__ = ("TTS",)


class TTS:
    __slots__ = ("_listening", "_tts",)

    def __init__(self) -> None:
        self._listening = threading.Event()
        self._listening.set()

        self._tts = SileroTTS(
            model_id="v5_ru",
            language="ru",
            speaker="baya",
            sample_rate=8000,
            device="cpu",
        )

    def to_voice(self, text: str) -> None:
        """Воспроизводит переданный текст.

        Args:
            text: Текст для воспроизведения.
        """
        self._listening.clear()
        
        try:
            filename = utils.generate_cached_speech_filename(text)
        
            if not os.path.exists(filename):
                self._tts.tts(text=text, output_file=filename)
        
            data, sample_rate = soundfile.read(filename)
        
            sounddevice.play(data, sample_rate)
            sounddevice.wait()
        finally:
            self._listening.set()
