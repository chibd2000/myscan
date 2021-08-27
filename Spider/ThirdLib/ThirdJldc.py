# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 0:01

from Spider.ThirdLib.Third import *


class Jldc(ThirdBase):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://jldc.me/anubis/subdomains/{}"
        self.source = 'jidc'

    def spider(self):
        print('Load Jidc api ...')
        try:
            resp = requests.get(url=self.addr.format(self.domain), headers=self.headers, verify=False, timeout=self.reqTimeout)
            text = resp.text
            results = re.findall(r'<th scope="row ">\d+</th>\n<td>(.*)</td>'.format(self.domain), text, re.S | re.I)
            if results:
                for _ in results:
                    self.resList.append(resp)
            else:
                print('Jldc API No Subdomains.')
        except Exception as e:
            print('[-] curl Jldc api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


# def do(domain):
#     pass
    # query = Jidc(domain)
    # return query.spider()


if __name__ == '__main__':
    pass
    # res = do('baidu.com') # ok
    # print(res)