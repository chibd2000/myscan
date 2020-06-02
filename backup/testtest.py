import requests
import re
import chardet

resp = requests.get('http://ids.nbcc.cn/1111111111111111111111111111111-index.html', allow_redirects=False)

print(resp.content)

if 'ThinkPHP' in resp.text or 'WE CAN DO IT JUST THINK' in resp.text:
    print("111111111")
