from angela_voice_assistant.core.routing import Router
from angela_voice_assistant.instances import tts
from angela_voice_assistant.modules.wiki import Wiki

wiki_router = Router()
wiki = Wiki()


@wiki_router.on_utterance(
    "расскижи о",
    "кто такой",
    "что такое",
    "поведай о",
    "разузнай кто такой",
    "расскижи то такой",
    "расскажи что такое",
    "поясни за",
    make_utterances_parameterized=True,
)
def search_in_wiki(question: str) -> None:
    tts.to_voice(wiki.search_in_wiki(question=question))
