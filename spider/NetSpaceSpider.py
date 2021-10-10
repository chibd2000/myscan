# coding=utf-8


from spider.public import *
from spider import BaseSpider
from lxml import etree
from core.MyRequest import *
from common.tools import *
from spider.common import config
from shodan import Shodan
import mmh3
import base64
import codecs

requests.packages.urllib3.disable_warnings()


class NetSpider(BaseSpider):
    def __init__(self, domain: str):
        super().__init__()
        self.source = 'Fofa & Shodan & Quake'
        self.domain = domain
        self.thread_list = []
        # &fields=host,title,ip,domain,port,server,protocol,city,as_number
        self.fofaAddr = "https://fofa.so/api/v1/search/all?email={FOFA_EMAIL}&key={API_KEY}&qbase64={B64_DATA}&size=10000&&fields=host,title,ip,domain,port,server,protocol,as_number"
        self.shodanAddr = "https://api.shodan.io/shodan/host/search?key={API_KEY}&query={QUERY}&minify=true&page=1"
        self.quakeAddr = "https://quake.360.cn/api/v3/search/quake_service"
        self.fofaApi = config.fofaApi
        self.fofaEmail = config.fofaEmail
        self.shodanApi = config.shodanApi
        self.quakeApi = config.quakeApi
        self.asnList = []
        self.ipList = []
        self.IpPortList = []
        self._init()

    def _init(self):
        self._getFaviconAndMD5()
        self._getBeianCompany()
        self.fofaKeywordList = ['domain="{}"'.format(self.domain), 'cert="{}"'.format(self.beian),
                                'host="{}"'.format(self.domain), 'icon_hash="{}"'.format(self.iconHash)]
        # self.quakeKeywordList = ['cert:"{}"'.format(self.beian)]
        self.quakeKeywordList = ['domain:"{}"'.format(self.domain), 'cert:"{}"'.format(self.beian),
                                 'host:"{}"'.format(self.domain), 'favicon:"{}"'.format(self.iconMD5)]
        self.shodanKeywordList = ['hostname:"{}"'.format(self.domain), 'ssl:"{}"'.format(self.domain),
                                  'http.favicon.hash:{}'.format(self.iconHash)]

    def _getFaviconAndMD5(self):
        try:
            resp = requests.get(getUrl(self.domain) + '/favicon.ico', headers=self.headers, allow_redirects=True, verify=False)
            if resp.status_code == 200:
                m1 = hashlib.md5()
                m1.update(resp.content)
                theMD5 = m1.hexdigest()
                favicon = codecs.encode(resp.content, 'base64')
                self.iconHash = mmh3.hash(favicon)
                self.iconMD5 = theMD5
                print('[+] get iconHash: ', self.iconHash)
                print('[+] get iconMD5: ', self.iconMD5)
            else:
                raise Exception
        except Exception as e:
            print('[-] _getFaviconAndMD5 first failed, error is {}'.format(e.args))
            print('[-] _getFaviconAndMD5 second ...')
            try:
                resp_ = requests.get(getUrl('www.' + self.domain) + '/favicon.ico', headers=self.headers, allow_redirects=True, verify=False)
                if resp_.status_code == 200:
                    m1_ = hashlib.md5()
                    m1_.update(resp_.content)
                    theMD5 = m1_.hexdigest()
                    favicon = codecs.encode(resp_.content, 'base64')
                    self.iconHash = mmh3.hash(favicon)
                    self.iconMD5 = theMD5
                    print('[+] get iconHash: ', self.iconHash)
                    print('[+] get iconMD5: ', self.iconMD5)
                else:
                    raise Exception
            except Exception as e:
                self.iconHash = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
                self.iconMD5 = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
                print('[-] _getFaviconAndMD5 second failed, error is {}'.format(e.args))

    def _getBeianCompany(self):
        try:
            beianAddr = 'https://icp.chinaz.com/home/info?host={}'
            response = requests.get(url=beianAddr.format(self.domain), headers=self.headers)
            html = etree.HTML(response.text)
            compangyName = html.xpath('/html/body/div/div[3]/div[1]/p[3]/text()')
            if compangyName == '':
                compangyName = 'xxxxxxxxxxxxxxx'
            self.beian = compangyName[0]
        except IndexError as e:
            self.beian = 'xxxxxxxxxxxxxxxxxxxxx'
            print('[-] curl beian no company, {}'.format(e.__str__()))
        except Exception as e:
            self.beian = 'xxxxxxxxxxxxxxxxxxxxx'
            print('[-] curl chinaz.com error, {}'.format(e.__str__()))

    # 保存文件
    def writeFile(self, web_lists: list, page: int):
        """
        [
        {'spider': 'fofa', 'subdomain': '123.123.123.124:22', 'title': '', 'ip': '123.123.123.124', 'domain': '', 'port': '22', 'web_service': '', 'port_service': 'SSH', 'search_keyword': 'ip="123.123.123.123/24" && port="22"'},
        {'spider': 'fofa', 'subdomain': '123.123.123.123:22', 'title': '', 'ip': '123.123.123.123', 'domain': '', 'port': '22', 'web_service': '', 'port_service': 'SSH', 'search_keyword': 'ip="123.123.123.123/24" && port="22"'}
         ]
        """
        workbook = openpyxl.load_workbook(os.getcwd() + os.path.sep + str(self.domain) + ".xlsx")
        worksheet = workbook.worksheets[page]  # 打开的是证书的sheet
        for i in web_lists:
            web = list()
            web.append(i['spider'])
            web.append(i['subdomain'])
            web.append(i['title'])
            web.append(i['ip'])
            web.append(i['domain'])
            web.append(i['port'])
            web.append(i['web_service'])
            web.append(i['port_service'])
            web.append(i['asn'])
            web.append(i['search_keyword'])
            worksheet.append(web)
        workbook.save(os.getcwd() + os.path.sep + str(self.domain) + ".xlsx")
        workbook.close()

    async def fofaDomainSpider(self):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            for keyword in self.fofaKeywordList:
                try:
                    domainList = []
                    res = await AsyncFetcher.fetch(session=session, url=self.fofaAddr.format(FOFA_EMAIL=self.fofaEmail,
                                                                                             API_KEY=self.fofaApi,
                                                                                             B64_DATA=base64.b64encode(
                                                                                                 keyword.encode()).decode()),
                                                   json=True)

                    for banner in res['results']:
                        if 'http' in banner[0]:
                            subdomain = banner[0].split('//')[1]  # https://www.baidu.com => www.baidu.com
                        else:
                            subdomain = banner[0]
                        if banner[6] == '':
                            portService = getPortService(banner[4])
                        else:
                            portService = banner[6]
                        subdomainInfo = {
                            'spider': 'FOFA',
                            'subdomain': subdomain,
                            'title': banner[1],
                            'ip': banner[2],
                            'domain': banner[3],
                            'port': banner[4],
                            'web_service': banner[5],
                            'port_service': portService,
                            'asn': banner[7],
                            'search_keyword': keyword
                        }
                        # print(subdomainInfo)
                        self.ipList.append(banner[2])
                        self.asnList.append(int(banner[7]))
                        self.resList.append(subdomain)
                        domainList.append(subdomainInfo)
                    # self.IpPortList
                    # [
                    #     {"ip": "1.1.1.1", "port": [7777, 8888]
                    #     {"ip": "2.2.2.2", "port": []
                    # ]
                    for i in domainList:
                        _ip = i['ip']
                        _port = i['port']
                        flag = True
                        for j in self.IpPortList:
                            if j['ip'] == i['ip']:
                                flag = False
                        if flag:
                            self.IpPortList.append({'ip': _ip, 'port': [int(_port)]})

                    for j in domainList:
                        _ip = j['ip']
                        _port = j['port']
                        if int(_port) == 443 or int(_port) == 80:
                            continue
                        flag = True
                        for k in self.IpPortList:
                            if k['ip'] == _ip:
                                for m in k['port']:
                                    if int(m) == int(_port):
                                        flag = False
                        if flag:
                            for p in self.IpPortList:
                                if p['ip'] == _ip:
                                    p['port'].append(int(_port))

                    self.writeFile(getUniqueList(domainList), 8)
                except Exception as e:
                    print('curl fofa.so api error, error is {}'.format(e.__str__()))

    async def quakeDomainSpider(self):
        headers = {"X-QuakeToken": self.quakeApi, "Content-Type": "application/json"}
        async with aiohttp.ClientSession(headers=headers) as session:
            for keyword in self.quakeKeywordList:
                try:
                    domainList = []
                    params = {'query': keyword, 'size': 500, 'ignore_cache': False}
                    res = await AsyncFetcher.postFetch2(session=session, url=self.quakeAddr, data=json.dumps(params),
                                                        json=True)
                    for banner in res['data']:
                        httpModule = banner['service'].get('name', '')  # http， http-simple-new
                        if 'http' in httpModule:
                            http = banner['service'].get('http')
                            if http:
                                subdomainInfo = {
                                    'spider': 'QUAKE',
                                    'subdomain': http['host'],
                                    'title': http['title'],
                                    'ip': banner['ip'],
                                    'domain': '',
                                    'port': banner['port'],
                                    'web_service': http['server'],
                                    'port_service': getPortService(banner['port']),
                                    'asn': banner['asn'],
                                    'search_keyword': keyword
                                }
                                # print(subdomainInfo)
                                if banner['ip'] == http['host']:
                                    self.ipList.append(banner['ip'])
                                    self.asnList.append(int(banner['asn']))
                                else:
                                    self.ipList.append(banner['ip'])
                                    self.asnList.append(int(banner['asn']))
                                    self.resList.append(http['host'])
                                domainList.append(subdomainInfo)
                        else:
                            subdomainInfo = {
                                'spider': 'QUAKE',
                                'subdomain': '',
                                'title': '',
                                'ip': banner['ip'],
                                'domain': '',
                                'port': banner['port'],
                                'web_service': '',
                                'port_service': getPortService(banner['port']),
                                'asn': banner['asn'],
                                'search_keyword': keyword
                            }
                            self.ipList.append(banner['ip'])
                            self.asnList.append(int(banner['asn']))
                            domainList.append(subdomainInfo)
                        for i in domainList:
                            _ip = i['ip']
                            _port = i['port']
                            flag = True
                            for j in self.IpPortList:
                                if j['ip'] == i['ip']:
                                    flag = False
                            if flag:
                                self.IpPortList.append({'ip': _ip, 'port': [int(_port)]})

                        # [{'ip':'1.1.1.1',}]
                        for j in domainList:
                            _ip = j['ip']
                            _port = j['port']
                            if int(_port) == 443 or int(_port) == 80:
                                continue
                            flag = True
                            for k in self.IpPortList:
                                if k['ip'] == _ip:
                                    for m in k['port']:
                                        if int(m) == int(_port):
                                            flag = False
                            if flag:
                                for p in self.IpPortList:
                                    if p['ip'] == _ip:
                                        p['port'].append(int(_port))
                    domainList = getUniqueList(domainList)
                    self.writeFile(domainList, 9)
                except Exception as e:
                    print('curl quake.360.cn api error, error is {}'.format(e.__str__()))

    async def shodanDomainSpider(self):
        # 这里用shodan模块的原因是正常请求会存在cloudflare，具体原因没研究，直接用shodan模块会方便
        api = Shodan(self.shodanApi)
        # ipinfo = api.host('8.8.8.8')
        for keyword in self.shodanKeywordList:
            try:
                domainList = []
                if keyword == 'ssl:"{}"'.format(self.domain):
                    countInfo = api.count(keyword)
                    if countInfo['total'] > 1000:
                        print('[-] shodan skip ssl search...')
                        continue
                # ssl:"zjhu.edu.cn" == ssl:"zjhu.edu.cn"
                # print(api.search_cursor(keyword))
                for banner in api.search_cursor(keyword):
                    # http exist
                    httpModule = banner['_shodan'].get('module', '')  # http， http-simple-new
                    if 'http' in httpModule:
                        http = banner.get('http', '')
                        if http:
                            subdomainInfo = {
                                'spider': 'SHODAN',
                                'subdomain': str(banner['hostnames']),
                                'title': http['title'],
                                'ip': banner['ip_str'],  # 不用host的原因是其中有时候存在域名的情况，自己这里需要把域名和IP分开收集
                                'domain': '',
                                'port': banner['port'],
                                'web_service': http['server'],
                                'port_service': getPortService(banner['port']),
                                'asn': banner['asn'][2:],
                                'search_keyword': keyword
                            }
                            # print(subdomainInfo)
                            self.ipList.append(banner['ip_str'])
                            self.asnList.append(int(banner['asn'][2:]))
                            for _ in banner['hostnames']:
                                self.resList.append(_)
                            domainList.append(subdomainInfo)
                    else:
                        subdomainInfo = {
                            'spider': 'SHODAN',
                            'subdomain': str(banner['hostnames']),
                            'title': '',
                            'ip': banner['ip_str'],  # 不用host的原因是其中有时候存在域名的情况，自己这里需要把域名和IP分开收集
                            'domain': '',
                            'port': banner['port'],
                            'web_service': '',
                            'port_service': getPortService(banner['port']),
                            'asn': banner['asn'][2:],
                            'search_keyword': keyword
                        }
                        # print(subdomainInfo)
                        self.ipList.append(banner['ip_str'])
                        self.asnList.append(int(banner['asn'][2:]))
                        if banner['hostnames']:
                            for _ in banner['hostnames']:
                                self.resList.append(_)
                        domainList.append(subdomainInfo)
                    for i in domainList:
                        _ip = i['ip']
                        _port = i['port']
                        flag = True
                        for j in self.IpPortList:
                            if j['ip'] == i['ip']:
                                flag = False
                        if flag:
                            self.IpPortList.append({'ip': _ip, 'port': [int(_port)]})

                    for j in domainList:
                        _ip = j['ip']
                        _port = j['port']
                        if int(_port) == 443 or int(_port) == 80:
                            continue
                        flag = True
                        for k in self.IpPortList:
                            if k['ip'] == _ip:
                                for m in k['port']:
                                    if int(m) == int(_port):
                                        flag = False
                        if flag:
                            for p in self.IpPortList:
                                if p['ip'] == _ip:
                                    p['port'].append(int(_port))
                self.writeFile(getUniqueList(domainList), 10)
            except Exception as e:
                print('curl shodan api error, error is {}'.format(e.__str__()))
            # async with aiohttp.ClientSession(headers=headers) as session:
            #     for keyword in self.shodanKeywordList:
            #         domainList = []
            #         async with session.get(url=self.shodanAddr.format(API_KEY=self.shodanApi, QUERY=quote(keyword)),
            #                                headers=self.headers, timeout=self.reqTimeout,
            #                                allow_redirects=True) as response:
            #             # res = await AsyncFetcher.fetch(session=session, , json=True) as response:
            #             print(await response.text(encoding='utf-8'))
            #             res = json.loads(await response.read())
            #             if int(res['matches']) < 1000:
            #                 for _ in res['matches']:
            #                     portService = getPortService(_['port'])
            #                     subdomainInfo = {
            #                         'spider': 'SHODAN',
            #                         'subdomain': _['hostnames'][0],
            #                         'title': _['title'],
            #                         'ip': _['ip_str'],
            #                         'domain': _['domains'],
            #                         'port': _['port'],
            #                         'web_service': _['product'],
            #                         'port_service': portService,
            #                         'asn': _['asn'][2:],
            #                         'search_keyword': keyword
            #                     }
            #
            #                     print(subdomainInfo)
            #                     self.ipList.append(_['ip_str'])
            #                     self.asnList.append(_['asn'][2:])
            #                     self.resList.append(_['hostnames'][0])
            #                     domainList.append(subdomainInfo)
            #                 domainList = getUniqueList(domainList)
            #                 self.writeFile(domainList, 5)

    # C段查询函数
    def fofaSegmentSpider(self, networksegment, page):
        cSegList = list()
        resp = requests.get(url=self.fofaAddr.format(self.fofaEmail, self.fofaApi, base64.b64encode(
            networksegment.encode()).decode()), headers=self.headers)

        try:
            json_data = resp.json()
            # 有两种情况
            #   1、API无效 json_data['results'] 直接报错，结果为KeyError: 'results'
            #   2、当前page中没有数据，则API有效 json_data['results']中的值为空列表[]
            temp_data = json_data['results']
            if len(temp_data) == 0:
                print("{} {} {} 无数据爬取! ".format('fofa', networksegment, page))
                return
        except KeyError:
            # KeyError 为 API无效
            print("API无效，请检查API是否有效！")
            return

        for i in json_data['results']:
            title, service, respContent = self.getTitleAndService(i[0], i[2])  # 请求标题与服务
            self.lock.acquire()
            self.resList.extend(self.matchSubdomain(self.domain, respContent))
            self.lock.release()
            re_ip = re.search(r'\d+.\d+.\d+:?\d?', i[0])  # 1.1.1.1:80 -> 1.1.1:80  http://1.1.1.1:80 -> 1.1.1.1:80
            if re_ip:
                self.resList.append(i[0])  # 只要是ip就添加到列表中
                domain = ''
            else:
                # 要探测的目标正好是在其中，比如 self.target = 'nbcc.cn'，那么子域名也就是nbcc.cn，如果目标是nbcc.edu.cn 那么直接就取 不跟下面的edu
                # gov继续判断，那么就是直接略过 print("原始爬取的网址为：" + str(i[0]))
                if self.domain in i[0]:
                    domain = self.domain
                    # print("1-处理过后的网址为：" + str(domain))
                # 特殊的edu gov的域名处理
                elif 'edu' in i[0] or 'gov' in i[0]:
                    domain_temp = i[0].split('.')
                    if len(domain_temp) >= 4:
                        domain = ".".join(domain_temp[len(domain_temp) - 3:])
                        # print("2-处理过后的网址为：" + str(domain))
                    else:
                        domain = i[0]
                        # print("3-处理过后的网址为：" + str(domain))
                else:
                    domain_temp = i[0].split('.')
                    if len(domain_temp) >= 3:
                        domain = ".".join(domain_temp[len(domain_temp) - 2:])
                        # print("4-处理过后的网址为：" + str(domain))
                    else:
                        domain = i[0].split('.', 1)[1]
                        # print("5-处理过后的网址为：" + str(domain))
                self.resList.append(i[0])  # 只要是域名就添加到列表中

            # if re.match(r'\d+.\d+.\d+', i[0].split('.', 1)[1]):
            #     domain = ''
            # else:
            #     domain = i[0].split('.', 1)[1]

            # if self.target in domain:
            #     self.task_queue.put(domain)

            ip_info = {
                'spider': 'FOFA',
                'subdomain': i[0],
                'title': title,
                'ip': i[1],
                'domain': domain,
                'port': i[2],
                'web_service': service,
                'port_service': getPortService(i[2]),
                'search_keyword': networksegment
            }

            # print(ip_info)

            cSegList.append(ip_info)
        self.lock.acquire()
        self.web_ip_lists_fofa.extend(cSegList)
        self.lock.release()

    def quakeSegmentSpider(self, networksegment, page):
        pass

    # shodan的线程处理函数
    def shodanSegmentSpider(self, networksegment, page):
        logging.info("Shodan Spider page {}".format(page))
        try:
            temp_list = list()
            resp = requests.get(url=self.shodanAddr.format(API_KEY=self.shodanApi, QUERY=networksegment, PAGE=page),
                                headers=self.headers)
            # 数据进行格式化
            json_data = resp.json()

            # 有两种情况
            #   1、API无效 json_data['results'] 直接报错，结果为KeyError: 'results'
            #   2、当前page中没有数据，则API有效 json_data['results']中的值为空列表[]
            temp_data = json_data['matches']
            if len(temp_data) == 0:
                print("{} {} {} 无数据爬取!".format('shodan', networksegment, page))
                return

            for i in json_data['matches']:
                self.resList.append(i['ip_str'])  # 只要是ip就添加到列表中

                try:
                    hostname = i['hostnames'][0]
                    self.resList.append(hostname)
                except KeyError as e:
                    hostname = ''

                #  获取其中的所有主键
                try:
                    product = i['product']
                except KeyError as e:
                    product = ''

                try:
                    title, service, RespOfTitleAndServer = self.getTitleAndService(hostname, i['port'])
                    self.resList.extend(self.matchSubdomain(self.domain, RespOfTitleAndServer))
                    # title = i['http']['title']
                except Exception as e:
                    title = ''

                try:
                    hostname = i['hostnames'][0]
                except KeyError as e:
                    hostname = ''

                try:
                    domains = ','.join(i['domains'])
                except KeyError as e:
                    domains = ''

                ip_info = {
                    'spider': 'Shodan',
                    'subdomain': hostname,
                    'title': title,
                    'ip': i['ip_str'],
                    'domain': domains,
                    'port': i['port'],
                    'web_service': product,
                    'port_service': getPortService(i['port']),
                    'search_keyword': networksegment
                }

                # 这里打印 进行测试数据
                print(ip_info)

                temp_list.append(ip_info)

                self.web_ip_lists_shodan.extend(temp_list)

        except IOError as e:
            print('[-] curl shodan.io error. {}'.format(e.__str__))

        except KeyError as e:
            # KeyError 为 API无效
            print("API次数已经用完 | API无效！")
            return

    # # fofa引擎的探测搜索ip段和域名
    # def fofa_ip_search(self, networksegment):
    #     # print(NetworkSegment)
    #     for page in range(1, config.fofa_page):  # 这里自定义页数
    #         self.thread_list.append(Thread(target=self.test01, args=(networksegment, page)))
    #
    #     for i in self.thread_list:
    #         i.start()
    #
    #     for i in self.thread_list:
    #         i.join()
    #
    # # shodan引擎的探测搜索ip段和域名
    # def shadon_ip_search(self, networksegment):
    #     # print(NetworkSegment)
    #     for page in range(1, config.shodan_page):
    #         self.thread_list.append(Thread(target=self.test02, args=(networksegment, page)))
    #
    #     for i in self.thread_list:
    #         i.start()
    #
    #     for i in self.thread_list:
    #         i.join()

    # async def fofaSpider(self):
    #     await self.fofaDomainSpider()
    #     await self.fofaSSLSpider()
    #     await self.fofaFaviconSpider()
    #
    # async def quakeSpider(self):
    #     await self.quakeDomainSpider()
    #     await self.quakeSSLSpider()
    #     await self.quakeFaviconSpider()
    #
    # async def shodanSpider(self):
    #     await self.shodanDomainSpider()
    #     await self.shodanSSLSpider()
    #     await self.shodanFaviconSpider()

    # 域名爬取处理函数
    async def spider(self):
        loop = asyncio.get_event_loop()
        taskList = [
            loop.create_task(self.shodanDomainSpider()),
            loop.create_task(self.quakeDomainSpider()),
            loop.create_task(self.fofaDomainSpider())
        ]
        await asyncio.gather(*taskList)

        # loop.create_task(self.quakeDomainSpider()),
        # loop.create_task(self.shodanDomainSpider())

        # await self.fofaDomainSpider()
        # await self.quakeDomainSpider()
        # 最后返回的是1、子域名:list 2、asn:list 3、ip存活段:dict

        # quakeIpList = self.quakeDomainSpider()
        # shodanIpList = self.shodanDomainSpider()

    # # 开始对ip的网段进行爬取
    # ip_list = Common_getIpSegment(ip_list)  # 对ip进行过滤
    # # print("=" * 30)
    # print(ip_list)
    # # print("=" * 30)
    # fofa_ip_list = ['ip="%s/24"' % i for i in ip_list]
    # shodan_ip_list = ['net:"%s/24"' % i for i in ip_list]
    # fofa_ip_list.extend(shodan_ip_list)

    # p = ThreadPoolExecutor(2)  # 因为是C段，所以这里使用线程池来进行分配
    # for i in fofa_ip_list:
    #     if 'ip=' in i:
    #         # continue
    #         p.submit(self.fofa_ip_search, i)  # 这里只查 ip="
    #         # pass
    #     else:
    #         p.submit(self.shadon_ip_search, i)  # 这里只查 net="
    # pass

    # 所有计划运行完毕，关闭结束线程池
    # p.shutdown()

    # 最后的FOFA和SHODAN的结果进行去重
    # self.write_file(self.web_ip_lists_fofa, self.domain, 3)
    # self.write_file(self.web_ip_lists_shodan, self.domain, 4)

    # results = [obj.result() for obj in web_ip_all_list]
    # for result in results:
    #     '''def write_file(self, web_lists, target):'''
    #     result = Common_getUniqueList(result)
    #     self.write_file(result, target, 3)
    # return ip_net

    # main start
    async def main(self):
        await self.spider()
        self.resList, self.asnList, self.ipList = list(set(self.resList)), list(set(self.asnList)), list(
            set(self.ipList))
        return self.resList, self.asnList, self.ipList, self.IpPortList


if __name__ == '__main__':
    start = time.time()
    NetSpider('zjhu.edu.cn').main()
    print(time.time() - start)
