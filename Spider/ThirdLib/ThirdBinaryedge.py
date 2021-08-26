# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 0:00

from Spider.ThirdLib.Third import *


class Binaryedge(ThirdBase):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://api.binaryedge.io/v2/query/domains/subdomain/{}"
        self.api = binaryedgeApi
        self.headers.update({'X-Key': self.api})

    def spider(self):
        print('Load Binaryedge api ...')
        try:
            resp = requests.get(url=self.addr.format(self.domain), headers=self.headers, verify=False, timeout=self.reqTimeout)
            text = resp.text
            results = re.findall(r'<th scope="row ">\d+</th>\n<td>(.*)</td>'.format(self.domain), text, re.S | re.I)
            if results:
                for _ in results:
                    self.resList.append(resp)
            else:
                print('Binaryedge API No Subdomains.')
        except Exception as e:
            print('[-] curl Binaryedge api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[{}] {}'.format(len(self.resList), self.resList))
        return self.resList


# def do(domain):
    # query = Binaryedge(domain)
    # return query.spider()

    # pass

if __name__ == '__main__':
    # res = do('baidu.com') # ok
    # print(res)
    pass