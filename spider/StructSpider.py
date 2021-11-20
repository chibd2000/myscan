# coding=utf-8
# @Author   : HengGe's team
# @Time     : 2021-08-25 1:15
from spider.public import *
from spider import BaseSpider
from core.utils.PorxyProvider import ProxyProvider


class CompanyStructSpider(BaseSpider):
    def __init__(self, domain, companyName):
        super().__init__()
        self.source = 'CompanyStructSpider'
        self.domain = domain
        self.companyName = companyName
        self.companyId = ''
        self.detailAddr = 'https://aiqicha.baidu.com/company_detail_{id}'  # 对应id详细的信息
        self.navigationAddr = 'https://aiqicha.baidu.com/compdata/navigationListAjax?pid={id}'  # 窗格信息
        self.investAddr = 'https://aiqicha.baidu.com/detail/investajax?p={page}&size=100&pid={id}'  # 对应id的公司投资信息
        self.holdAddr = "https://aiqicha.baidu.com/detail/holdsAjax?p={page}&size=100&pid={id}"  # 对应id公司的控股信息
        self.branchAddr = "https://aiqicha.baidu.com/detail/branchajax?p={page}&size=100&pid={id}"  # 对应id公司分支信息
        self.icpAddr = 'https://aiqicha.baidu.com/detail/icpinfoajax?p={page}&size=100&pid={id}'  # 对应id公司的备案信息
        self.appAddr = 'https://aiqicha.baidu.com/c/appinfoAjax?p={page}&size=100&pid={id}'  # 对应id公司的APP
        self.wxAddr = 'https://aiqicha.baidu.com/c/wechatoaAjax?p={page}&size=100&pid={id}'  # 对应id公司的微信公众号
        self.urlList = []  # 存储要异步操作的地址
        # self.proxyObject = ProxyProvider('"status":-1')

    def writeFile(self, web_lists, page):
        # CompanyName
        # mail
        # phone
        # company's domain
        try:
            workbook = openpyxl.load_workbook(os.getcwd() + os.path.sep + str(self.domain) + ".xlsx")
            worksheet = workbook.worksheets[page]  # 打开的是证书的sheet
            for i in web_lists:
                web = list()
                web.append(i['type'])
                web.append(i['entName'])
                web.append(i['information'])
                web.append(i['companyMail'])
                web.append(i['companyPhone'])
                web.append(i['companySite'])
                web.append(i['icp'])
                # web.append(i['app'])
                # web.append(i['wx'])
                worksheet.append(web)
            workbook.save(os.getcwd() + os.path.sep + str(self.domain) + ".xlsx")
            workbook.close()
        except Exception as e:
            print('[-] [{}] writeFile error, error is {}'.format(self.source, e.__str__()))

    def getCompanyPage(self):
        # t = self.proxyObject.getRandomOneProxy()
        # proxies = {
        #     'http': t,
        #     'https': t
        # }
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
                         "Zx-Open-Url": f"https://aiqicha.baidu.com/company_detail_{self.companyId}",
                         "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty",
                         "Referer": f"https://aiqicha.baidu.com/company_detail_{self.companyId}",
                         "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9",
                         "Connection": "close"}
        url = self.navigationAddr.format(id=self.companyId)
        try:
            html = requests.get(url=url, headers=burp0_headers, cookies=burp0_cookies)
            if html.status_code == 200:
                text = html.json()['data']
                for u in text[0]['children']:
                    if u['name'] == '对外投资':
                        print(u['name'], u['total'])
                        page = (u['total'] // 100 + 1) if (not u['total'] % 100) else (u['total'] // 100 + 2)
                        self.getInvestInformation(page)
                    elif u['name'] == '控股企业':
                        print(u['name'], u['total'])
                        page = (u['total'] // 100 + 1) if (not u['total'] % 100) else (u['total'] // 100 + 2)
                        self.getHoldingInformation(page)
                    elif u['name'] == '分支机构':
                        print(u['name'], u['total'])
                        page = (u['total'] // 100 + 1) if (not u['total'] % 100) else (u['total'] // 100 + 2)
                        self.getBranchInformation(page)

            # async with aiohttp.ClientSession() as session:
            #     async with session.get(url=self.navigationAddr.format(id=self.companyId), headers=burp0_headers,
            #                            cookies=burp0_cookies) as response:
            #         if response is not None and response.status == 200:
            #             text = await response.json(content_type='text/html', encoding='utf-8')
            #             for u in text['data'][0]['children']:
            #                 if u['name'] == '对外投资':
            #                     print(u['name'], u['total'])
            #                     page = (u['total'] // 100 + 1) if (not u['total'] % 100) else (u['total'] // 100 + 2)
            #                     await self.getInvestInformation(page, session)
            #                 elif u['name'] == '控股企业':
            #                     print(u['name'], u['total'])
            #                     page = (u['total'] // 100 + 1) if (not u['total'] % 100) else (u['total'] // 100 + 2)
            #                     await self.getHoldingInformation(page, session)
            #                 elif u['name'] == '分支机构':
            #                     print(u['name'], u['total'])
            #                     page = (u['total'] // 100 + 1) if (not u['total'] % 100) else (u['total'] // 100 + 2)
            #                     await self.getBranchInformation(page, session)

            #     elif u['name'] == '网站备案':
            #         print(u['name'], u['total'])
            #         page = (u['total'] // 100 + 1) if (not u['total'] % 100) else (u['total'] // 100 + 2)
            #         self.getICPInformation(page)
            # for p in data[4]['children']:
            #     if p['name'] == 'APP':
            #         print(p['name'], p['total'])
            #         page = (p['total'] // 100 + 1) if (not p['total'] % 100) else (p['total'] // 100 + 2)
            #         self.getAppInformation(page)
            #     elif p['name'] == '微信公众号':
            #         print(p['name'], p['total'])
            #         page = (p['total'] // 100 + 1) if (not p['total'] % 100) else (p['total'] // 100 + 2)
            #         self.getWxInformation(page)
        except Exception as e:
            print('[-] curl {} error, {}'.format(url, e.__str__()))

    def getInvestInformation(self, page):
        for _ in range(1, page):
            url = self.investAddr.format(id=self.companyId, page=str(_))
            self.getFirstInformation(url)

    def getHoldingInformation(self, page):
        for _ in range(1, page):
            url = self.holdAddr.format(id=self.companyId, page=str(_))
            self.getFirstInformation(url)

    def getBranchInformation(self, page):
        for _ in range(1, page):
            url = self.branchAddr.format(id=self.companyId, page=str(_))
            self.getFirstInformation(url)

    async def getDetailInformation(self, url, index, session, semaphore):
        async with semaphore:
            data = await self.getDetail(url, session)
            print(data)
            self.resList[index]['companyMail'] = str(data['companyMail'])
            self.resList[index]['companyPhone'] = str(data['companyPhone'])
            self.resList[index]['companySite'] = str(data['companySite'])

    async def getICPInformation(self, url, index, session, semaphore2):
        async with semaphore2:
            data = await self.getTwiceInformation(url, session)
            print(data)
            self.resList[index]['icp'] = str(data)

    async def getAppInformation(self, url, index, session):
        data = await self.getTwiceInformation(url, session)
        self.resList[index]['app'] = str(data)

    async def getWxInformation(self, url, index, session):
        data = await self.getTwiceInformation(url, session)
        self.resList[index]['wx'] = str(data)

    async def getCompanyInformation(self):
        taskList1 = []
        taskList2 = []
        # taskList3 = []]
        # taskList4 = []
        try:
            async with aiohttp.ClientSession() as session1:
                # 对应id的公司的电话/邮箱信息
                semaphore1 = asyncio.Semaphore(5)
                for index, value in enumerate(self.resList):
                    url = self.detailAddr.format(id=self.resList[index]['pid'])
                    taskList1.append(self.getDetailInformation(url, index, session1, semaphore1))
                await asyncio.gather(*taskList1)
        except Exception as e:
            print('[-] curl error, {}'.format(e.__str__()))

        try:
            async with aiohttp.ClientSession() as session2:
                # 对应id的公司的ICP
                semaphore2 = asyncio.Semaphore(5)
                for index, value in enumerate(self.resList):
                    url = self.icpAddr.format(page=str(1), id=self.resList[index]['pid'])
                    # print(url)
                    taskList2.append(self.getICPInformation(url, index, session2, semaphore2))
                await asyncio.gather(*taskList2)
        except Exception as e:
            print('[-] curl error, {}'.format(e.__str__()))

        # try:
        #     async with aiohttp.ClientSession() as session3:
        #         # 对应id的公司的APP
        #         for index, value in enumerate(self.resList):
        #             url = self.appAddr.format(page=str(1), id=self.resList[index]['pid'])
        #             taskList3.append(self.getAppInformation(url, index, session3))
        #         await asyncio.gather(*taskList3)
        # except Exception as e:
        #     print(e)
        #
        # try:
        #     async with aiohttp.ClientSession() as session4:
        #         # 对应id的公司的微信公众号
        #         for index, value in enumerate(self.resList):
        #             url = self.wxAddr.format(page=str(1), id=self.resList[index]['pid'])
        #             taskList4.append(self.getWxInformation(url, index, session4))
        #         await asyncio.gather(*taskList4)
        # except Exception as e:
        #     print(e)

    def getPerfectCompany(self):
        # t = self.proxyObject.getRandomOneProxy()
        # proxies = {
        #     'http': t,
        #     'https': t
        # }
        url = f'https://aiqicha.baidu.com/s?q={self.companyName}&t=0'
        # print(url)
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
        try:
            data = requests.get(url, headers=burp0_headers, cookies=burp0_cookies)
            html = data.text
            title = re.findall('queryStr":"(.*?)"', html)
            if len(title) > 0 and title[0].encode('utf-8').decode('unicode_escape') == self.companyName:
                pid = re.search('pid":"(.*?)"', html)
                self.companyId = pid.group(1)
                mainInfo = {
                    'type': '',
                    'entName': self.companyName,
                    'information': '',
                    'pid': self.companyId,
                }
                self.resList.append(mainInfo)
        except Exception as e:
            print(e, url)

    async def getDetail(self, url, session):
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
        try:
            async with session.get(url, headers=burp0_headers, cookies=burp0_cookies) as response:
                html = await response.text()
                # print(html)
                await asyncio.sleep(2)
                email = re.findall('email":"(.*?)"', html)
                telephone = re.findall('telephone":"(.*?)"', html)
                website = re.findall('website":"(.*?)"', html)
                return {
                    'companyMail': "".join(str(email)),
                    'companyPhone': "".join(telephone),
                    'companySite': "".join(website)
                }
        except Exception as e:
            print('[-] curl {} error, error is {}'.format(url, e.__str__()))

    # 一个调用接口，通过url来请求不同的接口来返回信息
    def getFirstInformation(self, url):
        # t = self.proxyObject.getRandomOneProxy()
        # proxies = {
        #     'http': t,
        #     'https': t
        # }
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
                   "Zx-Open-Url": f"https://aiqicha.baidu.com/company_detail_{self.companyId}",
                   "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty",
                   "Referer": f"https://aiqicha.baidu.com/company_detail_{self.companyId}",
                   "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "close"}
        try:
            data = requests.get(url, headers=headers, cookies=cookies)
            html = data.json()['data']
            if 'investajax' in url:
                # 对外投资
                for u in html['list']:
                    # detailUrl = self.detailAddr.format(id=u['pid'])
                    investInfo = {
                        'type': '对外投资',
                        'entName': u['entName'],
                        'information': '投资 ' + u['regRate'] + ' 状态 ' + u['openStatus'],
                        'pid': u['pid'],
                        # 'url': detailUrl
                    }
                    print(investInfo)
                    self.resList.append(investInfo)
            elif 'holdsAjax' in url:
                # 控股企业
                for u in html['list']:
                    # detailUrl = self.detailAddr.format(id=u['pid'])
                    holdInfo = {
                        'type': '控股企业',
                        'entName': u['entName'],
                        'information': '控股 ' + str(u['proportion']) + '%',  # 控股点数
                        'pid': u['pid'],
                        # 'url': detailUrl
                    }
                    print(holdInfo)
                    self.resList.append(holdInfo)
            elif 'branchajax' in url:
                # 分支机构
                for u in html['list']:
                    # detailUrl = self.detailAddr.format(id=u['pid'])
                    branchInfo = {
                        'type': '分支机构',
                        'entName': u['entName'],
                        'information': u['openStatus'],
                        'pid': u['pid'],
                        # 'url': detailUrl
                    }
                    print(branchInfo)
                    self.resList.append(branchInfo)
        except Exception as e:
            print('[-] curl {} error, error is {}'.format(url, e.__str__()))

    # 一个调用接口，通过url来请求不同的接口来返回信息
    async def getTwiceInformation(self, url, session):
        # proxies = self.proxyObject.getRandomOneProxy()
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
                   "Zx-Open-Url": f"https://aiqicha.baidu.com/company_detail_{self.companyId}",
                   "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty",
                   "Referer": f"https://aiqicha.baidu.com/company_detail_{self.companyId}",
                   "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "close"}
        try:
            async with session.get(url, headers=headers, cookies=cookies) as response:
                if response is not None and response.status == 200:
                    if 'icpinfoajax' in url:
                        # ICP备案信息
                        html = await response.json(content_type='text/html', encoding='utf-8')
                        print(url, html)
                        await asyncio.sleep(2)
                        return str([str(_['homeSite']) + '-' + str(_['icpNo']) for _ in html['data']['list']])
                    # elif 'appinfoAjax' in url:
                    #     # APP
                    #     html = await response.json(content_type='text/html', encoding='utf-8')
                    #     await asyncio.sleep(2)
                    #     return str([_['name'] for _ in html['data']['list']])
                    # elif 'wechatoaAjax' in url:
                    #     # 微信公众号
                    #     html = await response.json(content_type='text/html', encoding='utf-8')
                    #     await asyncio.sleep(2)
                    #     return str([_['wechatName'] for _ in html['data']['list']])
        except Exception as e:
            print('[-] curl {} error, error is {}'.format(url, e.__str__()))

    async def spider(self):
        # await self.proxyObject.getProxy()
        # # 1、获取符合度最大的一个公司的id（getPerfectCompany）
        # # 2、然后先获取自身（getPerfectCompany中的公司的id）相关的信息，比如 备案，微信，app，对外投资，控股企业，分支机构
        self.getPerfectCompany()
        # # 3、获取自己公司对外投资、分支机构、控股企业的对应的所有id，然后对其中获取的所有id进行去重
        self.getCompanyPage()
        print('[+] start collecting {} company'.format(self.companyName))
        # 4、遍历对外投资、分支机构、控股企业的所有去重的id列表，获取其中的 公司名称，公司官网，备案域名信息，联系人，邮箱，微信公众号，APP, 相关查询详细地址
        await self.getCompanyInformation()
        # 5、保存数据，self.writeFile
        self.writeFile(self.resList, 1)

    async def main(self):
        await self.spider()


if __name__ == '__main__':
    spider = CompanyStructSpider('huolala.cn', '浙江XXXX集团有限公司')
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(spider.main())
