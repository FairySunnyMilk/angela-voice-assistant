from ollama import chat
import time

system_prompt = """Ты - Анджела, голосовой помощник. 
Правила: 
- Отвечай максимум 15 словами
- Только на русском
- Без кода
- Дружелюбно"""

MODEL = "lakomoor/vikhr-llama-3.2-1b-instruct:1b"

print("🚀 Начинаем тест производительности Ollama\n")

# ЭТАП 1: Загрузка модели
print("📥 Загрузка модели...")
load_start = time.time()
init_response = chat(
    model=MODEL,
    messages=[{'role': 'user', 'content': 'init'}],
    keep_alive=-1
)
load_time = time.time() - load_start
print(f"✅ Модель загружена за {load_time:.2f} секунд\n")

# ЭТАП 2: Прогрев (первый реальный запрос всегда медленнее)
print("🔥 Прогрев модели (первый запрос)...")
warmup_start = time.time()
warmup_response = chat(
    model=MODEL,
    messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': 'Скажи "готово"'}
    ],
    keep_alive=-1
)
warmup_time = time.time() - warmup_start
print(f"✅ Прогрев завершен за {warmup_time:.2f} секунд")
print(f"Ответ прогрева: {warmup_response['message']['content']}\n")

# ЭТАП 3: Измерение скорости на 5 запросах
print("⚡ Измеряем скорость ответов...")
response_times = []

for i in range(5):
    query_start = time.time()
    response = chat(
        model=MODEL,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': f"Привет! Это тестовый запрос номер {i+1}"}
        ],
        keep_alive=-1
    ) 
    query_time = time.time() - query_start
    response_times.append(query_time)
    print(f"  Запрос {i+1}: {query_time:.2f} сек - {response['message']['content'][:50]}...")

# Статистика
avg_time = sum(response_times) / len(response_times)
print(f"\n📊 Статистика:")
print(f"  Среднее время ответа: {avg_time:.2f} сек")
print(f"  Минимальное: {min(response_times):.2f} сек")
print(f"  Максимальное: {max(response_times):.2f} сек")

# ЭТАП 4: Выгрузка модели
print("\n💾 Выгружаем модель...")
unload_start = time.time()
chat(
    model=MODEL,
    messages=[{'role': 'user', 'content': 'exit'}],
    keep_alive=0
)
print(f"✅ Выгружено за {time.time() - unload_start:.2f} сек")

print(f"\n⏱️ Общее время выполнения: {time.time() - load_start:.2f} сек")