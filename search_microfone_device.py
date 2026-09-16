import subprocess
import json


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

