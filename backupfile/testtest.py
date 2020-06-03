import requests
import re
requests.packages.urllib3.disable_warnings()



params = {'ecmsfrom': '8.8.8.8', 'show': 'none', 'keywords': 'ncist.edu.cn', 'page': 1}
resp = requests.post('https://www.dnsscan.cn/dns.html', data=params, verify=False)

a = re.findall(r'<a href="(.*?)"\srel', resp.text, flags=re.S)[1:]
print(a)
# print(resp.text)