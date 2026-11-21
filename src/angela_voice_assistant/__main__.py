import os

from angela_voice_assistant.answers import ANSWERS
from angela_voice_assistant.config import config
from angela_voice_assistant.handlers.base import base_router
from angela_voice_assistant.handlers.local_music import local_music_router
from angela_voice_assistant.handlers.timer import timer_router
from angela_voice_assistant.handlers.weather import weather_router
from angela_voice_assistant.handlers.wiki import wiki_router
from angela_voice_assistant.instances import assistant, dispatcher


def main() -> None:
    if not os.path.exists(config.CACHE_DIR):
        os.mkdir(config.CACHE_DIR)

    assistant.set_answers(ANSWERS)

    assistant.include_routers(
        base_router,
        local_music_router,
        timer_router,
        weather_router,
        wiki_router,
    )

    dispatcher.run()


if __name__ == "__main__":
    main()
