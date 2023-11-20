from video_parsing import pars
import time
import base64

b64 = ''
with open('test.mp4', 'rb') as f:
    data = f.read()
    b64 = base64.b64encode(data)

res = pars.delay(b64)

while not res.ready():
    print('waiting...')
    time.sleep(1)

print(res.get())

with open('test.mp3', 'wb') as f:
    f.write(base64.b64decode(res.get()))