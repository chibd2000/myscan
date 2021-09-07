# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-25 23:46

from spider.thirdLib.public import *
from spider.thirdLib import BaseThird


class Chinaz(BaseThird):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://api.sublist3r.com/search.php?domain={}"
        self.source = 'chinaz'

    async def spider(self):
        print('Load chinaz api ...')
        try:
            res = requests.get(url=self.addr.format(self.domain), headers=self.headers, verify=False,
                               timeout=self.reqTimeout)
            text = res.text
            if text != 'null':
                for subdomain in eval(text):
                    self.resList.append(subdomain)
            else:
                print('chinaz API No Subdomains.')
        except Exception as e:
            print('[-] curl chinaz.com api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[{}] {}'.format(len(self.resList), self.resList))
        return self.resList


# async def do(domain):
#     pass
# sublist3r = Sublist3r(domain)
# res = await sublist3r.spider()
# return res


if __name__ == '__main__':
    pass
    # do('baidu.com')
    # asyncio.run(do('baidu.com'))
    # asyncio.create_task(do('baidu.com'))
    # taskList = [asyncio.create_task(do('baidu.com'))]
    # loop = asyncio.get_event_loop()
    # res = loop.run_until_complete(asyncio.wait(*taskList))
    # print(res)
