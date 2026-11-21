import time
import webbrowser

from angela_voice_assistant.core.routing import Router
from angela_voice_assistant.handlers.local_music import local_music
from angela_voice_assistant.handlers.timer import off_timer
from angela_voice_assistant.instances import assistant, tts

base_router = Router()


@base_router.on_utterance("сколько времени", "который час")
def tell_time() -> None:
    tts.to_voice(str(time.strftime("%H часов %M минут")))


@base_router.on_utterance(
    "посмотри в интернете", 
    "найди в интернете", 
    "загугли", 
    "найди в поисковике", 
    "за гугле",
    make_utterances_parameterized=True,
)
def search_in_internet(query: str) -> None:
    webbrowser.open_new(f"https://www.google.com/search?client=firefox-b-d&channel=entpr&q={query}")


@base_router.on_utterance(
    "выключись", 
    "отключись", 
    "заверши работу", 
    "выход", 
    "закройся", 
    "прекрати работу", 
    "завершить работу", 
    "заверши работа", 
    "завершила работу", 
    "завершил работу",
    "завершена работа",
)
def off_assistant() -> None:
    assistant._is_working = False
    assistant.listening.clear()
    off_timer()
    local_music.off_music()
    assistant._local_llm.close_model()
