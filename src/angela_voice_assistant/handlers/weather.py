from angela_voice_assistant.core.routing import Router
from angela_voice_assistant.instances import tts
from angela_voice_assistant.modules.weather import WeatherVoice

weather_router = Router()
wv = WeatherVoice()


@weather_router.on_utterance(
    "какая погода", 
    "скажи какая погода",
    "скажи сейчас какая погода",
    "какая сейчас погода",
    "сейчас какая погода",
)
def weather() -> None:
    tts.to_voice(wv.get_weather())
