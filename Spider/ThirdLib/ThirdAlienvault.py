# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 0:13

from Spider.ThirdLib.Third import *


class Alien(ThirdBase):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://otx.alienvault.com/api/v1/indicators/domain/{}/passive_dns"

    def spider(self):
        print('Load otx.alienvault.com api ...')
        try:
            resp = requests.get(url=self.addr.format(self.domain), headers=self.headers, verify=False, timeout=self.reqTimeout)
            if 'No Captures found ' not in resp.text:
                for _ in resp.text.split('\n'):
                    self.resList.append(_)
            else:
                print('alienvault API No Subdomains.')
        except Exception as e:
            print('[-] curl otx.alienvault.com api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[{}] {}'.format(len(self.resList), self.resList))
        return self.resList


# def do(domain):
#     # query = Alien(domain)
#     # return query.spider()
#     pass


if __name__ == '__main__':
    # res = do('zjhzu.edu.cn') # not ok
    # print(res)
    pass