from angela_voice_assistant.core.routing import Router
from angela_voice_assistant.instances import assistant
from angela_voice_assistant.modules.music import LocalMusic

local_music_router = Router()

local_music = LocalMusic()


# @assistant.server_utterance()
# def run() -> None:
#     local_music.run()


@local_music_router.on_utterance(
    "останови музыку",
    "останови",
    "стоп",
    "пауза",
    "стал",
)
def pause() -> None:
    local_music.pause()


@local_music_router.on_utterance(
    "продолжи играть",
    "продолжил играть",
    "продолжи",
)
def unpause() -> None:
    local_music.unpause()


@local_music_router.on_utterance(
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


@local_music_router.on_utterance(
    "включи следующий трек",
    "следующий трек",
    "следующий",
)
def next() -> None:
    local_music.next()
