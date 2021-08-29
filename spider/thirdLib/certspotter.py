# coding=utf-8

from spider.thirdLib.third import *


class Certspotter(ThirdBase):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://api.certspotter.com/v1/issuances?domain={}&include_subdomains=true&expand=dns_names"

    def spider(self):
        print('Load certspotter api ...')
        try:
            resp = requests.get(url=self.addr.format(self.domain), headers=self.headers, verify=False,
                                timeout=self.reqTimeout)
            text = resp.text
            if 'not_allowed_by_plan' not in text:
                for _ in eval(text):
                    for subdomain in _['dns_names']:
                        if '*.' in subdomain:
                            subdomain = subdomain.replace('*.', '')
                        self.resList.append(subdomain)
            else:
                print('certspotter API No Subdomains.')
        except Exception as e:
            print('[-] curl certspotter api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[{}] {}'.format(len(self.resList), self.resList))
        return self.resList


# def do(domain):
#     query = Certspotter(domain)
#     return query.spider()


if __name__ == '__main__':
    # res = Certspotter('baidu.com').spider() #ok
    # print(res)
    pass
