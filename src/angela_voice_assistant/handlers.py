import time

from angela_voice_assistant.core import VoiceAssistant

assistant = VoiceAssistant()


@assistant.on_utterance("сколько времени", "который час")
def tell_time() -> None:
    assistant.speak(str(time.strftime("%H часов %M минут")))

# использование параметров
@assistant.on_utterance("найди в интернете")
def search_in_internet(query: str) -> None:
    ...

# Обработчик по умолчанию
@assistant.on_utterance()
def reply_with_llm(text: str) -> None:
    ...
