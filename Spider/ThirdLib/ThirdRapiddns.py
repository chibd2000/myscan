# coding=utf-8
from Spider.ThirdLib.Third import *


class Rapiddns(ThirdBase):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://rapiddns.io/subdomain/{}#result"

    def spider(self):
        print('Load rapiddns api ...')
        try:
            resp = requests.get(url=self.addr.format(self.domain), headers=self.headers, verify=False, timeout=self.reqTimeout)
            text = resp.text
            results = re.findall(r'<th scope="row ">\d+</th>\n<td>(.*)</td>'.format(self.domain), text, re.S | re.I)
            if results:
                for _ in results:
                    self.resList.append(resp)
            else:
                print('rapiddns API No Subdomains.')
        except Exception as e:
            print('[-] curl rapiddns api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[{}] {}'.format(len(self.resList), self.resList))
        return self.resList


# def do(domain):
#     query = Rapiddns(domain)
#     return query.spider()


if __name__ == '__main__':
    # res = do('baidu.com') # ok
    # print(res)
    pass