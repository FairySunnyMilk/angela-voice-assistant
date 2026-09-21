# Голосовой помощник Анджела 
### Данный проект был создан двумя дебилами, которым было нечем заняться, и не претендует ни на что, кроме вашего одобрения
#### Если вы хотите поддержать наш проект и дать нам возможность покушать то вам сюда [тык](https://boosty.to/two_idiots/donate)
### Ну а теперь переходим к установке и запуску 
## Загрузка
#### Клонируйте репозиторий
``` bash
git clone
```
#### Затем инициализируйте окружение, если у вас нет uv, то скачайте [тык](https://docs.astral.sh/uv/getting-started/installation/)
``` bash
uv sync
```
#### Для работы вым так же понадобиться установить некоторые стороние сервисы:
#### [![Ollama](https://img.shields.io/badge/ollama-%23000000.svg?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com/download)

#### Скачайте и разорхевируйте модель vosk [тык](https://github.com/kercre123/vosk-models/) или [тык](https://huggingface.co/alphacep/vosk-model-small-ru/tree/main)

#### После установки дополнительных сервисов и библиотек приступим к настройке и первому запуску Анджеллы
#### Для начала создаём файл `config.json`
``` bash
touch config.json
```
#### С такой структурой
``` json
{
"vosk_model": "",
"yandex_key": "",
"microphone": 0,
"speker": "",
"model_ollama": "",
"name_vois_assistant": ["\u0430\u043d\u0433\u0435\u043b\u043b\u0430", "\u0430\u043d\u0434\u0436\u0435\u043b\u043b\u0430", "\u0430\u043d\u0433\u0435\u043b\u0430", "\u0430\u043d\u0434\u0436\u0435\u043b\u0430", "\u0430\u043d\u0436\u0435\u043b\u043b\u0430", "\u0430\u043d\u0436\u0435\u043b\u0430", "\u0430\u043d\u0434\u0436\u0435\u043b\u0430", "\u0430\u043d\u0436\u0435\u043b\u043e", "\u0430\u043d\u0436\u0435\u043b\u043e\u0439"]
}
```
#### В vosk_model впишите полный путь до модели vosk
#### В yandex_key ключ, инструкцию для получения можно найти [здесь](https://github.com/MarshalX/yandex-music-api)
#### В microphone впишите индекс вашего микрофона, чтобы посмотреть доступных устройств запустите команду `python -m sounddevice` или запустите `uv run main.py -lm` и выберите из списка подходящий вам, так же можете выбрать микрофон по умолчанию командой `uv run main.py -m`
#### В speker впишите любого из списка `aidar, baya, kseniya, xenia, eugene`
#### В model_ollama любую из скаченных моделей. Список моделей можно посмотреть командой `ollama list`, если скаченных моделей нет, то у установите любую, которая подходит для вашего железа с сайта [ollama](https://ollama.com/search).
#### Если вы не хотите выбирать, то я рекомендую [lakomoor/vikhr-llama-3.2-1b-instruct:1b](https://ollama.com/lakomoor/vikhr-llama-3.2-1b-instruct)


### ![Ollama](https://img.shields.io/badge/ollama-%23000000.svg?style=for-the-badge&logo=ollama&logoColor=white)
### ![Python](https://img.shields.io/badge/python-%233670A0.svg?style=for-the-badge&logo=python&logoColor=ffdd54)
### ![Debian](https://img.shields.io/badge/Debian-%23D70A53.svg?style=for-the-badge&logo=debian&logoColor=white)
