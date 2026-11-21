import hashlib
import os

from angela_voice_assistant.config import config


def generate_cached_speech_filename(speech_text: str) -> str:
    """Генерирует хеш-имя файла для кеширования речи.

    Args:
        speech_text: Текст речи, на основе котрого создаётся хеш.

    Returns:
        Хеш-имя файла. Если файл речи с переданным текстом уже существует,
        то вернёт его имя.
    """
    text_hash = hashlib.md5(speech_text.encode("utf-8")).hexdigest()
    return os.path.join(config.CACHE_DIR, f"{text_hash}.wav")
