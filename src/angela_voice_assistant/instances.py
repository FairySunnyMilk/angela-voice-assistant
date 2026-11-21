from angela_voice_assistant.config import config
from angela_voice_assistant.core import (
    TTS,
    AssistantAddressFilter,
    Dispatcher,
    NotEmptyFilter,
    VoiceAssistant,
)
from angela_voice_assistant.modules.local_llm import LocalLLM

tts = TTS()
local_llm = LocalLLM(model_name=config.LLM_MODEL)
assistant = VoiceAssistant(
    tts,
    local_llm,
    AssistantAddressFilter(config.VOICE_ASSISTANT_NAME_VARIATIONS),
    NotEmptyFilter(),
)
dispatcher = Dispatcher(assistant)
