# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-25 23:53

from spider.thirdLib.third import *


class Securitytrails(ThirdBase):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'https://api.securitytrails.com/v1/domain/{}/subdomains'

    async def spider(self):
        print('Load securitytrails api ...')
        try:
            async with aiohttp.ClientSession() as session:
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain))
                results = re.findall(r'<th scope="row ">\d+</th>\n<td>(.*)</td>'.format(self.domain), text, re.S | re.I)
                if results:
                    for _ in results:
                        self.resList.append(_)
                else:
                    print('securitytrails API No Subdomains.')
        except Exception as e:
            print('[-] curl securitytrails api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [securitytrails] [{}] {}'.format(len(self.resList), self.resList))
        return self.resList


# def do(domain):
#     query = Securitytrails(domain)
#     return query.spider()


if __name__ == '__main__':
    pass
    # res = do('baidu.com') # ok
    # print(res)
