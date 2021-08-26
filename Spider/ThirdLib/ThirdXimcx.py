# coding=utf-8

from Spider.ThirdLib.Third import *


class Ximcx(ThirdBase):
    def __init__(self, domain):
        super().__init__()
        self.addr = 'http://sbd.ximcx.cn/DomainServlet'
        self.domain = domain

    def spider(self):
        print('Load ximcx api ...')
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        try:
            resp = requests.post(url=self.addr, data={'domain': self.domain}, headers=self.headers, verify=False, timeout=self.reqTimeout)
            text = resp.text
            results = json.loads(text)
            code = results['code']
            if code == 0:
                for _ in results['data']:
                    subdomain = _['domain']
                    self.resList.append(subdomain)
            else:
                print('ximcx API No Subdomains.')
        except Exception as e:
            print('[-] curl ximcx api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[{}] {}'.format(len(self.resList), self.resList))
        return self.resList


# def do(domain):
#     query = Ximcx(domain)
#     return query.spider()


if __name__ == '__main__':
    # res = do('baidu.com')  # ok
    # print(res)
    pass