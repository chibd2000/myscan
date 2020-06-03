from Config.config import *
from Spider.BaseSpider import *
import time

'''
POST /dns.html HTTP/1.1
Host: www.dnsscan.cn
Connection: close
Content-Length: 65
Cache-Control: max-age=0
Origin: https://www.dnsscan.cn
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Referer: https://www.dnsscan.cn/dns.html
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cookie: UM_distinctid=171cff332a91ed-04f923d6ec42fd-3a614f0b-1fa400-171cff332aa255; PHPSESSID=adb2ovkd17hg4e8iml77ucuamj; uid=36; token=06ee873b-2e57-40e3-832d-9d10584d7ab5; CNZZDATA1277897461=449359991-1588331755-%7C1591083588

ecmsfrom=8.8.8.8&show=none&keywords=tutorabc.com.cn&page=3
'''
class Qianxun(object):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.qianxunlist = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        }

    def spider(self):
        page = 1
        while True:
            time.sleep(1)
            params = {'ecmsfrom': '8.8.8.8', 'show': 'none', 'keywords': self.target, 'page': page}
            resp = requests.post('https://www.dnsscan.cn/dns.html', data=params, headers=self.headers, verify=False)
            re_data = re.findall(r'<a href="(.*?)"\srel', resp.text, flags=re.S)[1:]
            if re_data:
                self.qianxunlist.extend(re_data)
                print(re_data)
            else:
                return
            page += 1

    def main(self):
        logging.info("Qianxun Spider Start")
        self.spider()
        return self.qianxunlist


if __name__ == '__main__':
    qianxun = Qianxun('ncist.edu.cn')
    salist = qianxun.main()
    print(salist)



