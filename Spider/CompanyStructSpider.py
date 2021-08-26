# coding=utf-8
# @Author   : HengGe's team
# @Time     : 2021-08-25 1:15
from Spider.BaseSpider import *
import concurrent.futures
from tldextract import extract


class CompanyStructSpider(Spider):
    def write_file(self, web_lists, target, page):
        pass

    def spider(self):
        pass

    def main(self):
        pass

    def __init__(self):
        super().__init__()
        self.root_domain = set()
        self.save_name = ''
        self.urls = []
        self.qiye = []
        self.id = ''

    def put_s(self, url):
        mu = extract(url).domain + '.' + extract(url).suffix
        if mu not in self.root_domain and len(url) > 2:
            self.root_domain.add(mu)

    def put_list(self, urls):
        for url in urls:
            self.put_s(url)

    def save(self, key):
        name = self.save_name + '.json'
        with open(name, 'a', encoding='utf-8')as f:
            f.write(str(key) + '\n')

    def save_qiye(self, key):
        with open(self.save_name + '_企业架构' + '.txt', 'a', encoding='utf-8') as f:
            f.write(key + '\n')

    def page_list(self, id):
        url = 'https://aiqicha.baidu.com:443/compdata/navigationListAjax?pid=' + id
        try:
            burp0_cookies = {"BIDUPSID": "16D4BDA34A6BCEF90158A6794CEE2ECD", "PSTM": "1618912368",
                             "BAIDUID": "16D4BDA34A6BCEF9473327AF8F2CE8B7:FG=1",
                             "BAIDUID_BFESS": "16D4BDA34A6BCEF9473327AF8F2CE8B7:FG=1",
                             "__yjs_duid": "1_d553cc2d7f65d8229bffde018a438cc11627813889253",
                             "log_guid": "3404e8d605f152b3e17d8f36645f1182", "_j47_ka8_": "57",
                             "BDPPN": "8d6eccf33e5d9486638ce029fd9f2a86",
                             "Hm_lvt_ad52b306e1ae4557f5d3534cce8f8bbf": "1628739052,1628739086,1628818901,1628819094",
                             "_s53_d91_": "c3c1c9771394a94dd99450e38a95f9e0636fe7bddff00a043302444f0c9174f20bfff85c12d961e050f9e418097883bb2f47b28825e43976342e02f36ddba22c2884cbb81c6eb9cfabf26cfc70022c9c304fc3570ecef3510c28f391d1142986fbbee887cbe4cfd88a82a32019bb6eba9d9e0779581f4b0f8fe5dee714ec86115fc8897cf7c2ccb204e95045e4c4e8b5d9496cf7c92da213330839645dde0e7e744a2e3dcc5d667b9c8a194f9f17867dfc88be3e29f7ac02c5dc8c22e3f06809c271dca1a2b57c818a79d98823643474",
                             "_y18_s21_": "71555077",
                             "_fb537_": "xlTM-TogKuTwpt3Mi-%2AA3NL7fCYPEp5S6ZvFfsHeHGt1QQOYbTLf1UAmd",
                             "RT": "\"z=1&dm=baidu.com&si=16yko0n9fvi&ss=ksee565y&sl=0&tt=0&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf\""}
            burp0_headers = {"Sec-Ch-Ua": "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
                             "Accept": "application/json, text/plain, */*", "X-Requested-With": "XMLHttpRequest",
                             "Sec-Ch-Ua-Mobile": "?0",
                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
                             "Zx-Open-Url": f"https://aiqicha.baidu.com/company_detail_{self.id}",
                             "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty",
                             "Referer": f"https://aiqicha.baidu.com/company_detail_{self.id}",
                             "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9",
                             "Connection": "close"}
            html = requests.get(url, headers=burp0_headers, cookies=burp0_cookies)
            if html.status_code == 200:
                data = html.json()['data']
                for u in data[0]['children']:
                    if u['name'] == '对外投资':
                        print(u['name'], u['total'])
                        self.waitpi(id, u['total'])
                    elif u['name'] == '控股企业':
                        print(u['name'], u['total'])
                        self.kong(id, u['total'])
                    elif u['name'] == '分支机构':
                        print(u['name'], u['total'])
                        self.fgs(id, u['total'])
        except Exception as e:
            print(e, url, )

    def get_xinxi(self, url):
        try:
            xinxi = {}
            burp0_cookies = {"BIDUPSID": "16D4BDA34A6BCEF90158A6794CEE2ECD", "PSTM": "1618912368",
                             "BAIDUID": "16D4BDA34A6BCEF9473327AF8F2CE8B7:FG=1",
                             "BAIDUID_BFESS": "16D4BDA34A6BCEF9473327AF8F2CE8B7:FG=1",
                             "__yjs_duid": "1_d553cc2d7f65d8229bffde018a438cc11627813889253",
                             "log_guid": "3404e8d605f152b3e17d8f36645f1182", "_j47_ka8_": "57",
                             "BDPPN": "8d6eccf33e5d9486638ce029fd9f2a86",
                             "ZX_UNIQ_UID": "4ed9b259f13f700da6fb84fdc07d63a3",
                             "__yjs_st": "2_NzQxYmQ1NWQyZWM3OWI4YzZhNTUyYWI3OGZiZjk3NDUzMWMyMTA0YTQwMzU1YzEwZTQyYjk0M2I3MjNjOGYxYzViNzdlYzVlNjUwZjYyNmVmYWY4NTkxYzJmMDUwZjU3ZWRhNjk5MDJiNDgxMjQ5NzZiNjFiZDc2NjMxMzc3ODdiNDMzYjVlMzgwYWI1M2E3ZTg4Y2MwMDFiOWViNjIwZTIzYWUxZTNjODc0NjQ3NmE3OWY3NmNkNDIyYmJhMzgzNjA5NGQ4ZjNkZDgyODQzODg3NmVhMzU0YWUzYjIzNGVkYmVlMGUyOTg4ZWI4MmI3YzFkOGYyMDk3NGExNjU2ZF83X2ZiZjJhNTk3",
                             "_s53_d91_": "c3c1c9771394a94dd99450e38a95f9e0636fe7bddff00a043302444f0c9174f20bfff85c12d961e050f9e418097883bb2f47b28825e43976342e02f36ddba22c2884cbb81c6eb9cfabf26cfc70022c9c304fc3570ecef3510c28f391d1142986fbbee887cbe4cfd88a82a32019bb6eba9d9e0779581f4b0f8fe5dee714ec86115fc8897cf7c2ccb204e95045e4c4e8b5d9496cf7c92da213330839645dde0e7e744a2e3dcc5d667b9c8a194f9f17867d19058d554ae6c8e7df6d3a3e635823d9b03e6a8291eed5688896b0ac64cb1ceb",
                             "_y18_s21_": "ca104144",
                             "ab_sr": "1.0.1_ZWU4NjNiMjhjN2E5MTBlNjYxMmU3MGMxZTZjNjllYjJkMmQ4OTg0YmE3NDA4MDY0Mjc2MWYxNjZjYWMyMjhlNzE4ZDZiNjBhYzUyNmQxYWE3MDc4YmE2YTU0YzllYjdlYjdhN2M5NGM0NGU4ZGQzN2FkMTlkZTRiZTZlNDY4ODE0OTEwNjdiY2RiZGI4MjA4ZmVhZjYxMzM3ZGQzZjFiZA==",
                             "Hm_lvt_ad52b306e1ae4557f5d3534cce8f8bbf": "1628739052,1628739086,1628818901,1628819094",
                             "_fb537_": "xlTM-TogKuTwk4arcWuzlDAqtAWSNQceag4oOFXi9KAqrZkg1xe5V-Umd",
                             "Hm_lpvt_ad52b306e1ae4557f5d3534cce8f8bbf": "1628819340",
                             "RT": "\"z=1&dm=baidu.com&si=vrtrqtzuuz9&ss=ks9opsis&sl=6&tt=ca0p&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=abrr&ul=afrs\""}
            burp0_headers = {"Cache-Control": "max-age=0",
                             "Sec-Ch-Ua": "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"", "Sec-Ch-Ua-Mobile": "?0",
                             "Upgrade-Insecure-Requests": "1",
                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
                             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                             "Sec-Fetch-Site": "none", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1	",
                             "Sec-Fetch-Dest": "document", "Accept-Encoding": "gzip, deflate",
                             "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "close"}
            s = requests.session()
            s.keep_alive = False
            data = s.get(url, headers=burp0_headers, cookies=burp0_cookies, timeout=10)
            html = data.text
            title = re.findall('entName":"(.*?)"', html)
            title = title[0].encode('utf-8').decode('unicode_escape')
            email = re.findall('email":"(.*?)"', html)
            telephone = re.findall('telephone":"(.*?)"', html)
            website = re.findall('website":"(.*?)"', html)
            print(title, email, telephone, website)
            xinxi['公司名称'] = title
            xinxi['公司邮箱'] = "".join(email)
            xinxi['公司电话'] = "".join(telephone)
            xinxi['公司官网'] = "".join(website)
            mu = extract(website[0])
            self.root_domain.add(mu.domain + '.' + mu.suffix)
            self.save(xinxi)
        except  Exception as e:
            print(e, url)

    def get_name(self, name):
        self.save_name = name
        url = f'https://aiqicha.baidu.com/s?q={name}&t=0'
        try:
            burp0_cookies = {"BIDUPSID": "16D4BDA34A6BCEF90158A6794CEE2ECD", "PSTM": "1618912368",
                             "BAIDUID": "16D4BDA34A6BCEF9473327AF8F2CE8B7:FG=1",
                             "BAIDUID_BFESS": "16D4BDA34A6BCEF9473327AF8F2CE8B7:FG=1",
                             "__yjs_duid": "1_d553cc2d7f65d8229bffde018a438cc11627813889253",
                             "log_guid": "3404e8d605f152b3e17d8f36645f1182", "_j47_ka8_": "57",
                             "BDPPN": "8d6eccf33e5d9486638ce029fd9f2a86",
                             "ZX_UNIQ_UID": "4ed9b259f13f700da6fb84fdc07d63a3",
                             "__yjs_st": "2_NzQxYmQ1NWQyZWM3OWI4YzZhNTUyYWI3OGZiZjk3NDUzMWMyMTA0YTQwMzU1YzEwZTQyYjk0M2I3MjNjOGYxYzViNzdlYzVlNjUwZjYyNmVmYWY4NTkxYzJmMDUwZjU3ZWRhNjk5MDJiNDgxMjQ5NzZiNjFiZDc2NjMxMzc3ODdiNDMzYjVlMzgwYWI1M2E3ZTg4Y2MwMDFiOWViNjIwZTIzYWUxZTNjODc0NjQ3NmE3OWY3NmNkNDIyYmJhMzgzNjA5NGQ4ZjNkZDgyODQzODg3NmVhMzU0YWUzYjIzNGVkYmVlMGUyOTg4ZWI4MmI3YzFkOGYyMDk3NGExNjU2ZF83X2ZiZjJhNTk3",
                             "_s53_d91_": "c3c1c9771394a94dd99450e38a95f9e0636fe7bddff00a043302444f0c9174f20bfff85c12d961e050f9e418097883bb2f47b28825e43976342e02f36ddba22c2884cbb81c6eb9cfabf26cfc70022c9c304fc3570ecef3510c28f391d1142986fbbee887cbe4cfd88a82a32019bb6eba9d9e0779581f4b0f8fe5dee714ec86115fc8897cf7c2ccb204e95045e4c4e8b5d9496cf7c92da213330839645dde0e7e744a2e3dcc5d667b9c8a194f9f17867d19058d554ae6c8e7df6d3a3e635823d9b03e6a8291eed5688896b0ac64cb1ceb",
                             "_y18_s21_": "ca104144",
                             "ab_sr": "1.0.1_ZWU4NjNiMjhjN2E5MTBlNjYxMmU3MGMxZTZjNjllYjJkMmQ4OTg0YmE3NDA4MDY0Mjc2MWYxNjZjYWMyMjhlNzE4ZDZiNjBhYzUyNmQxYWE3MDc4YmE2YTU0YzllYjdlYjdhN2M5NGM0NGU4ZGQzN2FkMTlkZTRiZTZlNDY4ODE0OTEwNjdiY2RiZGI4MjA4ZmVhZjYxMzM3ZGQzZjFiZA==",
                             "Hm_lvt_ad52b306e1ae4557f5d3534cce8f8bbf": "1628739052,1628739086,1628818901,1628819094",
                             "_fb537_": "xlTM-TogKuTwk4arcWuzlDAqtAWSNQceag4oOFXi9KAqrZkg1xe5V-Umd",
                             "Hm_lpvt_ad52b306e1ae4557f5d3534cce8f8bbf": "1628819340",
                             "RT": "\"z=1&dm=baidu.com&si=vrtrqtzuuz9&ss=ks9opsis&sl=6&tt=ca0p&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=abrr&ul=afrs\""}
            burp0_headers = {"Cache-Control": "max-age=0",
                             "Sec-Ch-Ua": "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
                             "Sec-Ch-Ua-Mobile": "?0", "Upgrade-Insecure-Requests": "1",
                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
                             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                             "Sec-Fetch-Site": "none", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1	",
                             "Sec-Fetch-Dest": "document", "Accept-Encoding": "gzip, deflate",
                             "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "close"}
            data = requests.get(url, headers=burp0_headers, cookies=burp0_cookies)
            html = data.text
            title = re.findall('queryStr":"(.*?)"', html)
            if len(title) > 0 and title[0].encode('utf-8').decode('unicode_escape') == name:
                pid = re.search('pid":"(.*?)"', html)
                print(f"获取到需要爬取的公司信息:{name}")
                self.urls.append('https://aiqicha.baidu.com/company_detail_' + pid.group(1))
                return pid.group(1)
        except Exception as e:
            print(e, url)

    def pool(self, urls):
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(self.get, urls)

    def pool_get(self, defs, urls):
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(defs, urls)

    def get(self, url):
        try:
            start_urls = 'https://aiqicha.baidu.com/company_detail_'
            cookies = {"BIDUPSID": "16D4BDA34A6BCEF90158A6794CEE2ECD", "PSTM": "1618912368",
                       "BAIDUID": "16D4BDA34A6BCEF9473327AF8F2CE8B7:FG=1",
                       "BAIDUID_BFESS": "16D4BDA34A6BCEF9473327AF8F2CE8B7:FG=1",
                       "_fb537_": "xlTM-TogKuTwCF0ktHXhf1RsNlZSLn7cSoZILk3ubgBRMtJDRn8Ktpomd",
                       "__yjs_duid": "1_d553cc2d7f65d8229bffde018a438cc11627813889253",
                       "Hm_lvt_ad52b306e1ae4557f5d3534cce8f8bbf": "1627813890",
                       "Hm_lpvt_ad52b306e1ae4557f5d3534cce8f8bbf": "1627813890",
                       "ZX_UNIQ_UID": "b67971af26524441bd73785b27e88840",
                       "log_guid": "3404e8d605f152b3e17d8f36645f1182",
                       "__yjs_st": "2_YmEzMjM2MTE3MGRkYjhjODUwNWZkZDBiOWE5YzBmOTk2MjI3MTVkNGQ1ZmMyMTRlNzc2OGQ1MTkyMGIxNTQ1NWYxMjAxMGJkZGMzMjk4NmIwMjg3MWZiNDc3OGJhMGE1ZDNiOTFjNWM1NTY0MjQxMjZmYTAwMjAyMmNkMzk3ZjkzYmI0OWZiZTQ4ZjYzMjM4MTYzZTZjMGMwMTY1YzUzNjE4YzA3MTJlZjBhNGJiY2MwZDlkZjg2MDExNmYwOTNlMzc1Mjk4Y2UwOTMwMmYwM2UzOGRiMTg0NzFhYTEyYmNkZGNlZGRkMWYwMzQ2NzFhZTkwZWI5NzNjZWQwZTNhNDA4YWVhOGVlODRiOWE2NzRiZWJkMTQzM2YyMTlmMDVlXzdfZWZhYjQ0NGI=",
                       "ab_sr": "1.0.1_YWUxMGRjNzkxYTZiY2Y2MWNiOGUwYzgwNmNiZWNiOTk3NmYzNmExMTEyNGYwOGY2YzcyNjgyYWI2ZjQzMWZlZWEzZTg1MGRiNDYzMDI5MjQ4Mjg4ZTNhMzQ0ODc4ODJjYTdjMTI1MmYzZThjNzIwOGY0MWI0MGUxZWRmOTY1M2JiYTE3YTViNmIyOTIxNGU5OTgwYTc0NzUwMjQwZDkzOA==",
                       "_s53_d91_": "c3c1c9771394a94dd99450e38a95f9e0636fe7bddff00a043302444f0c9174f20bfff85c12d961e050f9e418097883bb2d4be21318633832263406b8b1811c8ab6f87e24aecc351330246d83706537d396744d3c200a5e8e3125684786bea09d72dffbf537324c0240eed660362653a6fc71d6b1eeee8807ceb46111e5665dcce6fd45e62f25dfcef7cd08858c6a1b6704d72d4c2840a86f2746ad642bea4dad78cc9244cb609c68cc85723a84e7833301d8a498a3aafa0a9e80476970797b7033698b6dc845ab7eb566770435acb79b",
                       "_j47_ka8_": "57", "_y18_s21_": "a610428f"}
            headers = {"Sec-Ch-Ua": "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
                       "Accept": "application/json, text/plain, */*", "X-Requested-With": "XMLHttpRequest",
                       "Sec-Ch-Ua-Mobile": "?0",
                       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36",
                       "Zx-Open-Url": f"https://aiqicha.baidu.com/company_detail_{self.id}",
                       "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty",
                       "Referer": f"https://aiqicha.baidu.com/company_detail_{self.id}",
                       "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "close"}
            data = requests.get(url, headers=headers, cookies=cookies)
            html = data.json()['data']
            if 'investajax' in url:
                for u in html['list']:
                    data = u['entName'] + "\t" + "投资" + u['regRate'] + '\t' + "状态" + u[
                        'openStatus'] + "\t" + start_urls + str(u['pid'])
                    self.save_qiye(data)
                    self.urls.append(start_urls + u['pid'])
            elif 'holdsAjax' in url:
                for u in html['list']:
                    data = u['entName'] + "\t" + "控股" + str(u['proportion']) + "\t" + start_urls + str(u['pid'])
                    self.save_qiye(data)
                    self.urls.append(start_urls + u['pid'])
            elif 'branchajax' in url:
                for u in html['list']:
                    data = u['entName'] + "\t" + "状态" + u['openStatus'] + '\t' + start_urls + str(u['pid'])
                    self.save_qiye(data)
                    self.urls.append(start_urls + u['pid'])
        except Exception as e:
            print(e, url)

    def waitpi(self, id, page):
        urls = []
        for ur in range(1, int(page // 10) + 1):
            url = f"https://aiqicha.baidu.com/detail/investajax?p={str(ur)}&size=10&pid={str(id)}"
            urls.append(url)
        self.pool(urls)

    def kong(self, id, page):
        urls = []
        for ur in range(1, int(page // 10) + 1):
            url = f"https://aiqicha.baidu.com/detail/holdsAjax?pid={str(id)}&p={str(ur)}&size=10"
            urls.append(url)
        self.pool(urls)

    def fgs(self, id, page):
        urls = []
        for ur in range(1, int(page // 10) + 1):
            url = f"https://aiqicha.baidu.com/detail/branchajax?p={str(ur)}&size=10&pid={str(id)}"
            urls.append(url)
        self.pool(urls)

    def start(self, name):
        id = self.get_name(name)
        self.id = id
        self.page_list(id)
        print(f"开始收集{name}下属公司")
        self.pool_get(self.get_xinxi, self.urls)
        print(self.root_domain)


if __name__ == '__main__':
    data = CompanyStructSpider()
    # 公司全称
    data.start("吉利集团有限公司")

if __name__ == '__main__':
    pass
