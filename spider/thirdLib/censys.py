# coding=utf-8
from spider.thirdLib.public import *
from spider.thirdLib import BaseThird

# Censys还没写上去
class Censys(BaseThird):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'https://censys.io/'
        self.id = config.censysId
        self.secret = config.censysSecret

    def spider(self):
        data = {
            'query': f'parsed.names: {self.domain}',
            'page': 1,
            'fields': ['parsed.subject_dn'],
            'flatten': True}
        resp = requests.post(self.addr, json=data, auth=(self.id, self.secret))
        if not resp:
            return
        data = resp.json()
        status = data.get('status')
        if status != 'ok':
            logger.log('ALERT', status)
            return
        subdomains = self.match(self.domain, str(data))
        self.resList = self.resList.union(subdomains)
        pages = data.get('metadata').get('pages')
        for page in range(2, pages + 1):
            time.sleep(self.delay)
            data['page'] = page
            resp = requests.post(self.addr, json=data, auth=(self.id, self.secret))
            if not resp:
                return
            subdomains = self.match(self.domain, str(resp.json()))
            self.resList = self.resList.union(subdomains)
        self.resList = list(set(self.resList))
        return self.resList


# def do(domain):
#     query = Censys(domain)
#     return query.spider()


if __name__ == '__main__':
    pass
    # do('zjhzu.edu.cn')
