import requests
import pymorphy3
from num_to_rus import Converter

from angela_voice_assistant.MyLogging import logging

LOG = logging('log')

@LOG.log_class()
class WeatherVoice:
    """Формирует текст текущей погоды, пригодный для озвучки голосовым помощником."""
    """Модуль был частично написан ИИ и не является финально рабочей версией, просим прощения, если будет замечена его некоректная работа или сбои."""
    WIND_DIRECTIONS_16 = {
        "N": "север", "NNE": "северо-северо-восток", "NE": "северо-восток",
        "ENE": "востоко-северо-восток", "E": "восток", "ESE": "востоко-юго-восток",
        "SE": "юго-восток", "SSE": "юго-юго-восток", "S": "юг",
        "SSW": "юго-юго-запад", "SW": "юго-запад", "WSW": "западо-юго-запад",
        "W": "запад", "WNW": "западо-северо-запад", "NW": "северо-запад",
        "NNW": "северо-северо-запад",
    }

    def __init__(self, city: str = "Санкт-Петербург", timeout: int = 10):
        self.city = city
        self.timeout = timeout
        self._conv = Converter()

        self.url = f'https://wttr.in/{self.city}?format=j1&lang=ru'

        self.morth = pymorphy3.MorphAnalyzer()

    # ---------- служебные ----------

    def _plural(self, n: int, forms: tuple[str, str, str]) -> str:
        """forms = (один, два, пять). Возвращает нужную форму для числа n."""
        n = abs(int(n)) % 100
        if 11 <= n <= 19:
            return forms[2]
        n %= 10
        if n == 1:
            return forms[0]
        if 2 <= n <= 4:
            return forms[1]
        return forms[2]

    def _temp_words(self, t: float) -> str:
        """+7 -> 'плюс семь градусов', -3 -> 'минус три градуса'."""
        t = int(round(t))
        forms = ("градус", "градуса", "градусов")
        if t > 0:
            return f"плюс {self._conv.convert(t)} {self._plural(t, forms)}"
        if t < 0:
            return f"минус {self._conv.convert(abs(t))} {self._plural(abs(t), forms)}"
        return "ноль градусов"

    def _wind_ru(self, code: str) -> str:
        return self.WIND_DIRECTIONS_16.get(code.upper(), code.lower())

    # ---------- публичный API ----------
    def fetch(self, url: str) -> dict:
        """Загружает JSON с wttr.in."""
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def speak(self, rec: dict) -> str:
        """Возвращает готовую фразу для озвучки по JSON-ответу wttr.in."""
        cur = rec["current_condition"][0]

        temp       = float(cur["temp_C"])
        feels      = float(cur["FeelsLikeC"])
        humidity   = int(round(float(cur.get("humidity", "0"))))
        pressure   = int(round(float(cur["pressure"])))
        precip     = float(cur["precipMM"])
        visibility = int(round(float(cur["visibility"])))
        uv         = int(round(float(cur.get("uvIndex", "0"))))
        weather    = cur["lang_ru"][0]["value"].lower()
        wind       = self._wind_ru(cur["winddir16Point"])
        wind_speed = int(round(float(cur["windspeedKmph"])))

        parts = [f"Сейчас в {self.morth.parse(self.city)[0].inflect({'loct'}).word} {weather}."]
        parts.append(f"Температура {self._temp_words(temp)}.")
        parts.append(f"Ощущается как {self._temp_words(feels)}.")
        parts.append(
            f"Влажность {self._conv.convert(humidity)} "
            f"{self._plural(humidity, ('процент', 'процента', 'процентов'))}."
        )

        if wind_speed:
            parts.append(
                f"Ветер с {wind}а, {self._conv.convert(wind_speed)} "
                f"{self._plural(wind_speed, ('километр', 'километра', 'километров'))} в час."
            )
        else:
            parts.append("Ветер слабый, штиль.")

        parts.append(
            f"Давление {self._conv.convert(pressure)} "
            f"{self._plural(pressure, ('гектопаскаль', 'гектопаскаля', 'гектопаскалей'))}."
        )
        parts.append(
            f"Видимость {self._conv.convert(visibility)} "
            f"{self._plural(visibility, ('километр', 'километра', 'километров'))}."
        )

        if precip <= 0:
            parts.append("Осадков нет.")
        else:
            mm = max(1, int(round(precip)))
            parts.append(
                f"Осадки {self._conv.convert(mm)} "
                f"{self._plural(mm, ('миллиметр', 'миллиметра', 'миллиметров'))}."
            )

        parts.append(f"УФ-индекс {self._conv.convert(uv)}.")
        return " ".join(parts)

    def get_weather(self) -> str:
        rec_json = self.fetch(self.url)
        return self.speak(rec_json)