import time
import webbrowser

from angela_voice_assistant.core import VoiceAssistant

assistant = VoiceAssistant()


@assistant.on_utterance("сколько времени", "который час")
def tell_time() -> None:
    assistant.speak(str(time.strftime("%H часов %M минут")))


@assistant.on_utterance(
    "посмотри в интернете", 
    "найди в интернете", 
    "загугли", 
    "найди в поисковике", 
    "за гугле",
)
def search_in_internet(query: str) -> None:
    webbrowser.open_new(f"https://www.google.com/search?client=firefox-b-d&channel=entpr&q={query}")


@assistant.on_utterance()
def reply_with_llm(text: str) -> None:
    ...


# Выключение Ассистента
@assistant.on_utterance('выключись', 
                        'отключись', 
                        'заверши работу', 
                        'выход', 
                        'закройся', 
                        'прекрати работу', 
                        'завершить работу', 
                        'заверши работа', 
                        'завершила работу', 
                        'завершил работу')
def off_assistent():
    assistant.processing_utterances.clear()
    assistant.listening.clear()
    off_timer()
    local_music.off_local_music()
    

"""timer"""
# TODO: Добавить докстринг
from queue import Queue

from Levenshtein import distance

from angela_voice_assistant.time_fraze import dict_time

q_timer = Queue()


@assistant.server_utterance()
def run_server() -> None:
    while True:
        command = str(q_timer.get())
        
        if command == "-1":
            break
        if command.isdigit:
            assistant.speak('Таймер запущен')
            time.sleep(int(command))
            assistant.speak("Таймер остановлен")


def get_time_from_str(text: str) -> int:
    for lt, it in dict_time.items():
        if any([distance(text, h) < 2 for h in lt]):
            return it
    else:
        return 0


@assistant.on_utterance(
    "таймер",
    "поставь таймер",
    "запусти таймер",
)
def on_timer(text: str) -> None:
    text_time = get_time_from_str(text)
    q_timer.put(str(text_time))


def off_timer() -> None:
    q_timer.put("-1")


"""timer"""

"""wiki search"""

import wikipediaapi
import pymorphy3

morfh = pymorphy3.MorphAnalyzer()

def normal_wive(text:str) -> str:
    return " ".join([morfh.parse(word)[0].normal_form for word in text.split()])


@assistant.on_utterance('расскижи о',
                        "кто такой",
                        "что такое",
                        "поведай о",
                        "разузнай кто такой",
                        "расскижи то такой",
                        "расскажи что такое",
                        "поясни за")
def search_in_wiki(question:str) -> None:
    question = normal_wive(question)
    wiki_wiki = wikipediaapi.Wikipedia(
            user_agent="MyWikiBot/1.0 (contact: myemail@example.com)",
            language="ru"
            )   
    page = wiki_wiki.page(question)
    if page.exists():
        assistant.speak(page.summary.split('\n')[0])
    else:
        page = wiki_wiki.page(question.split()[-1])
        if page.exists():
            assistant.speak(page.summary.split('\n')[0])
        else:
            assistant.speak('Я не нашла информацию по вашему запросу')



"""
local_music
"""

from angela_voice_assistant.music import LocalMusic

local_music = LocalMusic()


@assistant.server_utterance()
def run() -> None:
    local_music.run()


@assistant.on_utterance('останови музыку',
                        'останови',
                        'стоп',
                        'пауза',
                        'стал')
def pause() -> None:
    local_music.pause()


@assistant.on_utterance('продолжи играть',
                        'продолжил играть',
                        'продолжи')
def unpause() -> None:
    local_music.unpause()


@assistant.on_utterance(
    "включи скачанные треки",
    "запусти скачанные треки",
    "проиграй скачанные треки",
    "включи скачанные музыку",
    "включи скачиваю музыку",
    "включи мою волну",
    "включи музыку",
    "выключи мою волну",
    "выключи музыку",
)
def play() -> None:
    local_music.play()


@assistant.on_utterance('включи следующий трек',
                        'следующий трек',
                        'следующий')
def next() -> None:
    local_music.next()