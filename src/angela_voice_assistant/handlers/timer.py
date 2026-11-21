import time
from queue import Queue

from Levenshtein import distance

from angela_voice_assistant.core.routing import Router
from angela_voice_assistant.instances import assistant, tts
from angela_voice_assistant.time_fraze import dict_time

timer_router = Router()

q_timer = Queue()


@assistant.server_utterance()
def run_server() -> None:
    while True:
        command = str(q_timer.get())
        
        if command == "-1":
            break
        if command.isdigit():
            tts.to_voice('Таймер запущен')
            time.sleep(int(command))
            tts.to_voice("Таймер остановлен")


def get_time_from_str(text: str) -> int:
    for lt, it in dict_time.items():
        if any([distance(text, h) < 2 for h in lt]):
            return it
    
    return 0


@timer_router.on_utterance(
    "таймер",
    "поставь таймер",
    "запусти таймер",
    make_utterances_parameterized=True,
)
def on_timer(text: str) -> None:
    text_time = get_time_from_str(text)
    q_timer.put(str(text_time))


def off_timer() -> None:
    q_timer.put("-1")
