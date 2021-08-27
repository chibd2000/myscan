# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 0:10

from Spider.ThirdLib.Third import *


class Threatbook(ThirdBase):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "http://www.sitedossier.com/parentdomain/{}"

    def spider(self):
        print('Load sitedossier api ...')
        try:
            resp = requests.get(url=self.addr.format(self.domain), headers=self.headers, verify=False,
                                timeout=self.reqTimeout)
            text = resp.text
            results = re.findall(r'<a href="/site/(.*\.{})">'.format(self.domain), text)
            if results:
                for _ in results:
                    self.resList.append(_)
            else:
                print('sitedossier API No Subdomains.')
        except Exception as e:
            print('[-] curl sitedossier api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[{}] {}'.format(len(self.resList), self.resList))
        return self.resList


# def do(domain):
#     query = Threatbook(domain)
#     return query.spider()


if __name__ == '__main__':
    pass
    # res = do('zjhzu.edu.cn') # ok
    # print(res)