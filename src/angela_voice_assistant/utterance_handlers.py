import time

from angela_voice_assistant.assistant import VoiceAssistant

assistant = VoiceAssistant()


@assistant.on_utterance("сколько времени", "который час")
def tell_time() -> None:
    assistant.speak(str(time.strftime("%H часов %M минут")))
