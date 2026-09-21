#!venv/bin/python

from local_llm import model

from yandex_music import Client
from vosk import Model, KaldiRecognizer
from threading import Thread
from translate import Translator
from pyperclip import paste
from num_to_rus import Converter
from memory_profiler import profile
from retry_requests import retry
from silero_tts.silero_tts import SileroTTS
import sys
import os
import queue
import json
import sys
import json
import time
import sounddevice as sd
import soundfile as sf
import random
import webbrowser
import shutil
import soundfile as sf
import subprocess
from Levenshtein import distance as dis



class Angella():
    def __init__(self):
        self.function = {
                    ('посмотри в интернете',
                     'найди в интернете',
                     'загугли',
                     'найди в поисковике',
                     'за гугле'): self.search_in_internet,
                    ("скачай музыку",
                     "установи музыку"): self.start_download_music_from_user_likes,
                    ('включи мою волну',
                     'включи музыку'): self.on_my_wave,
                    ('выключи мою волну',
                     'выключи музыку'): self.off_my_wave,
                    ('включи следующий трек',
                     'следующий трек',
                     'следующий'): self.play_next_track,
                    ('включи скачанные треки',
                     'запусти скачанные треки',
                     'проиграй скачанные треки',
                     'включи скачанные музыку',
                     'включи скачиваю музыку'): self.on_play_downloab_music,
                    ('включи разговор',
                     'включи диалог'): self.on_tolking_for_LLM,
                    ('выключи разговор',
                     'выключи диалог'): self.off_tolking_for_LLM,
                    ('останови музыку',
                     'останови',
                     'стоп',
                     'пауза',
                     'стал'): self.stop_music,
                    ('продолжи играть',
                     'продолжил играть',
                     'продолжи'): self.unstop_music,
                    ('переведи',
                     'перевиди'): self.translate,
                    ('сколько времени',
                      'который час'): self.what_time,
                    ('выключись',
                     'прекрати работать',
                     'прекрати работу'): self.off_angella,
                    ('включи ключ фразу',
                     'активируй ключ фразу'): self.on_key_fraze,
                    ('выключи ключ фразу'): self.off_key_fraze,
                    ('таймер',
                     "включи таймер",
                     "останови таймер",
                     "останови время"): self.timer,
                    ("перезагрузись",
                     "перезагрузить"): self.restart,
                }
        
        
        self.fraze = {
                    ("привет", "здравствуй"): ("привет чем могу помочь", "здравствуйте как я могу вам помочь"),
                    ("как дела", "как настроение"): ("спасибо, у меня все отлично а у вас", "все хорошо, готов к вашим вопросам"),
                    ("спасибо", "благодарю"): ("н+е за что", "всегда рада помочь"),
                    ("до свидания", "пока"): ("до свидания", "пока хорошего дня"),
                    ("ты меня слышишь", "ты работаешь"): ("да, я вас слышу", "да, я здесь"),
                    ("кто ты", "что ты такое"): ("я голосовой помощник анджелла, разработанный для помощи пользователям", "я виртуальный помощник анджелла"),
                    ("молодец"): ('я стараюсь вам угодить', 'я стараюсь вам угодить'),
                }
        
        self.browser = {
                    'yandex': 'https://ya.ru/search/?text=',
                    'google': 'https://www.google.com/search?q=',
                    'bing': 'https://www.bing.com/search?q=',
                    'DuckDuckGo': 'https://duckduckgo.com/?ia=web&origin=funnel_home_website&t=h_&q=',
        
                }

        self.check_args()
        
        with open("config.json", "r", encoding="utf-8") as file:
            config = json.load(file)[0]
            self.name_vois_assistant = config['name_vois_assistant']
            self.yandex_api_key = config['yandex_key']
            self.vosk_model:str = config['vosk_model']
            self.microphone = config['microphone']
            self.speker = config['speker']
            self.model_ollama = config['model_ollama']
        try:
            self.client = Client(self.yandex_api_key).init()
        except:
            print("Проблемы с подключением к интернету, проверьте подключение и перезапустите помощника")
        self.LLM = model(model_name=self.model_ollama)
        self.global_text = ""
        self.listened_tracks = []
        self.messages = []
        self.over_track = True
        self.pause = False
        self.li_mu = True
        self.tolking = False
        self.next_track = False
        self.make_last_track = False
        self.work = True
        self.key = False
        self.last_time = 0
        self.timer_on = False


        self.tts = SileroTTS(model_id='v5_ru', language='ru', speaker=self.speker, sample_rate=8000, device='cpu')

        self.listening = True

    # start tts
    def number_to_text(self, text: str) -> str:
        conv = Converter()
        text = list(text.split())
        sign = ''
        for word in text:
            if word[0] == '-':
                sign = 'минус '
            if word.replace(',','').replace('-','').isdigit():
                text[text.index(word)] = str(sign + str(conv.convert(abs(int(word.replace(',',''))))))
            sign = ''
        text = ' '.join(text)
        return text

    def on_tts(self, text):
        self.listening = False
        text = self.number_to_text(text)
        print(text)
        self.global_text = ''
        self.stop_music("")
        if not os.path.exists('last_tts'):
                    os.mkdir('last_tts')
        if not os.path.exists(fr'last_tts/{text.replace(' ','_')}.mp3'):
            self.tts.tts(text=text, output_file=fr'last_tts/{text.replace(' ','_')}.mp3')
        data, fs = sf.read(fr'last_tts/{text.replace(' ','_')}.mp3')
        sd.play(data, fs)
        time.sleep((len(data) / fs) * 2)
        sd.stop()
        time.sleep(0.1)

        self.listening = True
        self.global_text = ''
        self.unstop_music("")

    def text_to_speech(self, text):
        t = Thread(target=self.on_tts, args=[text])
        t.start()
        t.join()
    # over tts

    # start stt
    @profile
    def stt(self):
        model = Model(self.vosk_model)  # полный путь к модели

        samplerate = 44100

        device = int(self.microphone)

        q = queue.Queue()

        def q_callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))

        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device, dtype='int16', channels=1, callback=q_callback):
            rec = KaldiRecognizer(model, samplerate)
            while self.work:
                if self.listening:
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        text = json.loads(rec.Result())["text"]
                        if text != '' and text != "input overflow" and self.listening:
                            self.global_text = text
                            print(text)
    # over stt

    # star functions of music
    def start_download_music_from_user_likes(self, *args):
        t1 = Thread(target=self.download_music_from_user_likes)
        t1.start()
    
    def download_music_from_user_likes(self, *args):
        errors = 0
        n = 1
        try:
            tracks = self.client.usersLikesTracks().tracks
            all_ = len(tracks)
            if not os.path.exists('music'):
                os.mkdir('music')
            for track in tracks:
                if not self.work:
                    break
                print(f'{track.fetch_track().title} = {n} of {all_}')
                if not os.path.exists(f'music/{track.fetch_track().title}.mp3') and not os.path.exists(f'music/track{tracks.index(track)+1}.mp3'):
                    try:
                        track.fetch_track().download(f'music/{track.fetch_track().title}.mp3')
                    except:
                        track.fetch_track().download(f'music/track{tracks.index(track)+1}.mp3')
                        print(Exception)
                        errors += 1
                n += 1
            self.text_to_speech('му+зыка ска+чана')
        except Exception as e:
            print(e)
            self.write_errors(e, 'download_music_from_user_likes')
            print(errors)

    def play_music(self, file:str, last_track=None):
        shutil.copy(file, 'track_play.mp3')
        audio_data, audio_samplerate = sf.read(file=file)
        size_music = (len(audio_data) / audio_samplerate)
        print(size_music)
        sd.play(data=audio_data, samplerate=audio_samplerate)
        i = 0
        start_m = time.time()
        end_m:int
        while i < 400 and self.work:
            time.sleep(size_music/400)
            if not self.li_mu or self.next_track:
                sd.stop()
                break
            if not self.pause:
                i += 1
            elif self.pause:
                end_m = time.time()
                sd.stop()
                while self.pause and self.work:
                    ...
                sd.play(data=audio_data[audio_samplerate*int(end_m-start_m):], samplerate=audio_samplerate)
        sd.stop()
        os.remove(file)
        self.next_track = False
        self.listened_tracks.append(last_track)


    def my_wave(self):
        print(42)
        try:
            try:
                next_track = random.choice(self.client.usersLikesTracks()).fetch_track().id
            except:
                next_track = '80292164'
            while self.li_mu and self.work:
                similar_traks = self.client.tracks_similar(track_id=str(next_track))
                dt = random.choice(similar_traks.similar_tracks)
                name = str(dt.title) + '.mp3'
                next_track = self.client.tracks_similar(track_id=str(dt.track_id)).similar_tracks[0].track_id
                dt.download(name)
                print(dt.title)
                self.play_music(name, last_track=dt)
                print(dt.title)
        except Exception as e:
            self.text_to_speech('Возни+кла пробле+ма с прои+грыванием му+зыки, я пе+резапускаю програ+мму')
            print(e)
            self.write_errors(e, 'my_wave')
            self.my_wave()

    def play_next_track(self, *args):
        self.next_track = True

    def off_my_wave(self, *args):
        self.li_mu = False
        time.sleep(1)
        self.text_to_speech('я вы+ключила му+зыку')
        self.li_mu = True

    @profile
    def play_downloab_music(self):
        try:
            downloab_music = os.listdir('music')
            random.shuffle(downloab_music)
            for track in downloab_music:
                print(track)
                self.play_music(f'music/{track}', f'music/{track}')
                if not self.li_mu:
                    break

        except Exception as e:
            print(e)
            self.write_errors(e, 'play_downloab_music')
            self.text_to_speech('Там ничего нет или возникла ошибка')

    def on_play_downloab_music(self, *args):
        t1 = Thread(target=self.play_downloab_music)
        t1.start()

    def on_my_wave(self, *args):
        t1 = Thread(target=self.my_wave, args=())
        t1.start()

    def stop_music(self, *args):
        try:
            self.pause = True
        except:
            ...

    def unstop_music(self, *args):
        try:
            self.pause = False
        except:
            ...
    # over functions of music

    # system functions
    def check_args(self):
        args = sys.argv[1::]
        if args:
            if '-h' in args or '--help' in args:
                print('''
-h, --help - список команд
-v, --vois - список голосов
-c, --command - список голосовых команд
-b, --browser - список доступных поисковых систем
-m - установить микрофон по умолчанию
-lm - вывести список устройств для ввода аудио
                    ''')
            if '-v' in args or '--vois' in args:
                print('aidar, \nbaya, \nkseniya, \nxenia, \neugene')
            if '-c' in args or '--command' in args:
                for c in list(self.function.keys()):
                    print(c)
            if '-b' in args or '--browser' in args:
                print('\n'.join(list(self.browser.keys())))
            if '-m' in args:
                com = subprocess.run(["python", "-m", "sounddevice"], capture_output=True, text=True)
                list_device = str(com.stdout).split("\n")
                global_id = 0
                for id, dev in enumerate(list_device):
                    if '*' in dev:
                        global_id = id
                        break
                with open("config.json", "r") as f:
                    m = json.load(f)
                    rec_dev = int(m[0]['microphone'])
                print(f'Id if choice device: {rec_dev}, id of recomended device {global_id}')
                if rec_dev != global_id:
                    m[0]['microphone'] = global_id
                    with open("config.json", "w", encoding='utf-8') as f:
                        json.dump(m, f)
            if '-lm' in args:
                com = subprocess.run(["python", "-m", "sounddevice"], capture_output=True, text=True)
                list_device = str(com.stdout)
                print(list_device)
            return False
        else:
            return True
    
    def write_errors(self, error, name_function):
        with open('errors.txt', '+a', encoding='utf-8') as file:
            file.write(f'{time.strftime('%H часов %M минут %S секунд')}  {name_function}  errors == {str(error)} \n')

    def copi_from_paste(self):
        return str(paste())

    def on_tolking_for_LLM(self, *args):
        self.tolking = True
        print(self.tolking)

    def off_tolking_for_LLM(self, *args):
        self.tolking = False
        print(self.tolking)

    def off_angella(self, *args):
        self.LLM.close_model()
        self.li_mu = False
        self.work = False

    def key_fraze(self):
        if (0 <= int(time.time()) - self.last_time <= 5) or self.key or any([dis(self.global_text.split()[0], f) <= 2 for f in self.name_vois_assistant]):
                self.last_time = int(time.time())
                return True

    
    def on_key_fraze(self, *args):
        self.key = False

    def off_key_fraze(self, *args):
        self.key = True

    def restart(self, *args):
        self.off_my_wave('')
        os.system("uv run start.py")
        self.off_angella("")
    # # # # # # # # # # # #

    # angell's functions    
    def timer(self, *args):
        try:
            if self.timer_on:
                self.text_to_speech(f"Таймер остановлен, прошедшее время {int(time.time()) - self.start_time} секунд")
                self.timer_on = False
            else:
                self.text_to_speech("Таймер запущен")
                self.start_time = int(time.time())
                self.timer_on = True
        except Exception as e:
            print(e)
            self.write_errors(e, 'timer')


    def translate(self, *args):
        try:
            self.text_to_speech(str(Translator(to_lang='ru').translate(self.copi_from_paste())))
        except Exception as e:
            print(e)
            self.write_errors(e, 'translate')
            self.text_to_speech('прошу прощение возникла проблема с подключением к переводчику')

    def explain_meaning(self, *args): #подразумевал "объясни значение"
        word = self.copi_from_paste()
        self.text_to_speech(self.LLM.generate(fr'объясни значение слова {word}'))

    def what_time(self, *args):
        self.text_to_speech(str(time.strftime('%H часов %M минут %S секунд')))

    def search_in_internet(self, text, br='yandex'):
        for q in list(self.function.keys())[0]:
            text = str(text).replace(q, '')
        webbrowser.open(f'{self.browser[br]}{text}')

    # # # # # # # # # # # #


    @profile
    def processing_requests(self):
        while self.work:
            if self.global_text != '' and self.key_fraze():
                if self.key_fraze():
                    self.global_text = self.global_text.replace(str(self.global_text.split()[0]) + ' ','')
                try:
                    work = True
                    for fs in self.fraze:
                        if self.global_text in fs or dis(self.global_text, fs)/len(fs) < 0.2:
                            print(55)
                            self.text_to_speech(str(random.choice(self.fraze[fs])))
                            work = False
                            break
                    if work:
                        for fs in self.function:
                            for ffs in fs:
                                if (ffs in self.global_text or dis(ffs, self.global_text)/len(self.global_text) < 0.2) and len(ffs)>5:
                                    print(ffs, fs)
                                    print(66)
                                    self.function[fs](self.global_text)
                                    self.global_text = ''
                                    work = False
                    if self.tolking and work and self.global_text != '':
                        print(789)
                        self.text_to_speech(self.LLM.generate(self.global_text))
                except Exception as e:
                    print(e)
                    self.write_errors(e, 'processing_requests')

    @profile
    def main(self):
        t1 = Thread(target=self.stt)
        t2 = Thread(target=self.processing_requests)

        t1.start()
        t2.start()

        t1.join()
        t2.join()


if __name__ == '__main__':
    A = Angella()
    A.main()