from ollama import chat
import json
import os


class model():
    def __init__(self, model_name):
        self.model_name = model_name
        self.rule = system_prompt = """Ты - Анджела, голосовой помощник. 
                                        Правила: 
                                        - Отвечай максимум 15 словами
                                        - Только на русском
                                        - Без кода
                                        - Дружелюбно"""
        print("Инициализация модели:")
        print("Запуск локального сервера:")
        #os.system("ollama serve &")
        init_response = chat(
                            model=model_name,
                            messages=[{'role': 'user', 'content': 'init'}],
                            keep_alive=-1
                            )
        print("Конец инициализации")

    def generate(self, prompt):
        response = chat(
            model=self.model_name,
            messages=[
                {'role': 'system', 'content': self.rule},
                {'role': 'user', 'content': prompt}
            ],
            keep_alive=-1
        )
        return response['message']['content']
    def close_model(self):
        chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': 'exit'}],
                keep_alive=0
            )

def main():
    with open('config.json', 'r', encoding='utf-8') as f:
        n = json.load(f)[0]['model_ollama']
    m = model(model_name=n)
    print(m.generate("Привет моя дорогая"))

if __name__ == "__main__":
    main()