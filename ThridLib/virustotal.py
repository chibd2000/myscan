import time
from Spider.BaseSpider import *


'''
最多查询100条
'''


class VirusTotal(object):
    def __init__(self, domain):
        self.source = 'VirusTotalQuery'
        self.module = 'Intelligence'
        self.addr = 'https://www.virustotal.com/ui/domains/{}/subdomains'
        self.domain = domain
        self.subdomainlist = list()

    def query(self):
        next_cursor = ''
        while True:
            time.sleep(1)
            headers = {'Referer': 'https://www.virustotal.com/', 'TE': 'Trailers'}
            params = {'limit': '40', 'cursor': next_cursor}
            resp = requests.get(url=self.addr.format(self.domain), headers=headers, params=params)
            if not resp:
                return
            data = resp.json()
            subdomains = list()
            datas = data.get('data')

            if datas:
                for data in datas:
                    subdomain = data.get('id')
                    if subdomain:
                        subdomains.append(subdomain)
            else:
                break

            self.subdomainlist.extend(subdomains)
            print(self.subdomainlist)
            meta = data.get('meta')
            if meta:
                next_cursor = meta.get('cursor')
            else:
                break

    def main(self):
        logging.info("VirusTotalSpider Start")
        self.query()
        return self.subdomainlist


if __name__ == '__main__':
    VirusTotal('tutorabc.com.cn').main()
