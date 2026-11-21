from pathlib import Path

import sounddevice as sd
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    PATH: str = Path(__file__).resolve().parent.parent.parent

    VOSK_MODEL_PATH: str= f"{PATH}/models/vosk-model-small-ru-0.22"
    
    print(f"VOSK_MODEL_PATH: {VOSK_MODEL_PATH}")
    
    VOSK_SAMPLE_RATE: int = 16000
    VOSK_MICROPHONE_NUMBER: int = -1
    
    if VOSK_MICROPHONE_NUMBER == -1:
        VOSK_MICROPHONE_NUMBER = sd.query_devices(device="default")["index"]
    
    LLM_MODEL: str = "lakomoor/vikhr-llama-3.2-1b-instruct:1b"

    CACHE_DIR: str = f"{PATH}/cache"

    VOICE_ASSISTANT_NAME_VARIATIONS: tuple[str, ...] = (
        "ангелла",
        "анджелла",
        "ангела",
        "анджела",
        "анжелла",
        "анжела",
        "анжело",
        "анжелой",
        "от жалость",
        "также она",
        "анджела очка",
        "анжелу осечка",
        "моя дорогая",
        "моя девочка",
        "анджелу осечка",
        "да ласточка",
        "моя заинька",
        "наша заинька",
        "милочка",
        "моя милочка",
        "лапочка",
        "лампочка",
        "моя лапочка",
        "моя лапой",
        "моя душенька",
        "душенька",
        "им душенька",
        "энджела",
        "анжелы",
    )

    SPEED_ANSWER: tuple[str, ...] = (
        "Говорите",
        "Что вы хотели?",
        "Чем могу помочь?",
    )


config = Config()
