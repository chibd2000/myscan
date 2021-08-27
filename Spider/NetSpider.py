# coding=utf-8

from spider.BaseSpider import *
from threading import Thread
from spider import config
from bs4 import BeautifulSoup
import base64
import codecs
import hashlib
import mmh3


class HackRequest(object):
    def __init__(self, domain, cookie=None, hash=None, md5=None):
        self.domain = domain
        self.cookie = cookie
        self.iconHash = hash
        self.iconMD5 = md5

    async def getRequest(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    text = await resp.text()
                    title = self._getTitle(text).strip().replace('\r', '').replace('\n', '')
                    status = resp.status
                    return title, status, resp
        except Exception as e:
            return e

    def _getFaviconAndMD5(self):
        resp = requests.get(self.getUrl(self.domain))
        m1 = hashlib.md5()
        m1.update(resp.content)
        theMD5 = m1.hexdigest()
        favicon = codecs.encode(resp.content, 'base64')
        self.iconHash = mmh3.hash(favicon)
        self.iconMD5 = theMD5

    def _getHeaders(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/68.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) '
            'Gecko/20100101 Firefox/68.0',
            'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/68.0']
        ua = random.choice(user_agents)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,'
                      'application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Referer': 'https://www.google.com/',
            'User-Agent': ua,
            'Upgrade-Insecure-Requests': '1',
            'X-Forwarded-For': '127.0.0.1',
        }
        return headers

    def _getTitle(self, markup):
        soup = BeautifulSoup(markup, 'lxml')

        title = soup.title
        if title:
            return title.text

        h1 = soup.h1
        if h1:
            return h1.text

        h2 = soup.h2
        if h2:
            return h2.text

        h3 = soup.h3
        if h2:
            return h3.text

        desc = soup.find('meta', attrs={'name': 'description'})
        if desc:
            return desc['content']

        word = soup.find('meta', attrs={'name': 'keywords'})
        if word:
            return word['content']

        text = soup.text
        if len(text) <= 200:
            return text
        return ''

    def getUrl(self, domain):
        if 'http://' in domain or 'https://' in domain:
            return f'{domain}'
        else:
            if ':443' in domain:
                return f'https://{domain}'

            if ':80' in domain:
                return f'http://{domain}'

            return f'http://{domain}'


class NetSpider(Spider):
    def __init__(self, domain):
        super().__init__()
        self.source = 'Fofa & Shodan & Quake'
        self.domain = domain
        self.net_list = list()  # 存放所有爬取到的url
        self.web_domain_lists = list()  # 存放域名信息的的列表
        self.web_ip_lists_shodan = list()  # shodan存放ip信息的列表
        self.web_ip_lists_fofa = list()  # fofa存放ip信息的列表
        self.web_ip_lists_qauke = list()  # fofa存放ip信息的列表
        self.thread_list = list()
        self.fofaAddr = "https://fofa.so/api/v1/search/all?email={FOFA_EMAIL}&key={API_KEY}&qbase64={B64_DATA}&size=100"
        self.shodanAddr = "https://api.shodan.io/shodan/host/search?key={API_KEY}&query={QUERY}&minify=true&page={PAGE}"
        self.quakeAddr = "https://quake.360.cn/api/v3/search/quake_service"
        self.fofaApi = config.fofaApi
        self.fofaEmail = config.fofaEmail
        self.shodanApi = config.shodanApi
        self.quakeApi = config.quakeApi
        self.request = HackRequest(domain)
        self.csegmentList = []
        self.faviconList = []

    # 保存文件
    def writeFile(self, web_lists, page):
        """
    [
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
            web.append(i['search_keyword'])
            worksheet.append(web)
        workbook.save(os.getcwd() + os.path.sep + str(self.domain) + ".xlsx")
        workbook.close()

    def fofaDomainSpider(self):
        ipList = []  # 存储存在的ip网段 /24
        domain_word = 'domain="%s"' % self.domain
        try:
            resp = requests.get(
                url=self.fofaAddr.format(FOFA_EMAIL=self.fofaEmail, API_KEY=self.fofaApi, B64_DATA=base64.b64encode(
                    domain_word.encode()).decode()), headers=self.headers)
            json_data = resp.json()
            for i in json_data['results']:
                title, service, respContent = self.getTitleAndService(i[0], i[2])
                self.lock.acquire()
                self.net_list.extend(self.matchSubdomain(self.domain, respContent))
                self.lock.release()
                re_ip = re.match(r'\d+.\d+.\d+:?\d?', i[0])  # 1.1.1.1:80 -> 1.1.1:80
                if re_ip:
                    self.net_list.append(i[0])  # 只要是ip就添加到列表中
                    domain = ''
                else:
                    if self.domain in i[0]:
                        domain = self.domain
                    else:
                        domain = ''

                    self.net_list.append(i[0])  # 只要是域名就添加到列表中

                ipList.append(i[1])
                sub_domain = i[0]
                if 'http' in i[0]:
                    sub_domain = i[0].split('//')[1]  # https://www.baidu.com => www.baidu.com

                subDomainInfo = {
                    'spider': 'FOFA',
                    'subdomain': sub_domain,
                    'title': title,
                    'ip': i[1],
                    'domain': domain,
                    'port': i[2],
                    'web_service': service,
                    'port_service': getPortService(i[2]),
                    'search_keyword': domain_word
                }

                print(subDomainInfo)

                self.web_domain_lists.append(subDomainInfo)
        except Exception as e:
            pass

        self.web_domain_lists = getUniqueList(self.web_domain_lists)
        self.lock.acquire()
        self.writeFile(self.web_domain_lists, 3)
        self.lock.release()
        return ipList

    def quakeDomainSpider(self):
        ipList = []
        headers = {"X-QuakeToken": "9fd0da05-93f9-49d2-b5e5-d43243268e80",
                   "Content-Type": "application/json"}
        params = {'query': 'domain: "{}"'.format(self.domain), 'size': 500, 'ignore_cache': False}
        resp = requests.post(url=self.quakeAddr, headers=headers, data=json.dumps(params))
        print(resp.text)
        return ipList

    def shodanDomainSpider(self):
        shodanIpList = []
        return shodanIpList

    # C段查询函数
    def fofaSegmentSpider(self, networksegment, page):
        logging.info("Fofa Spider Page {}".format(page))
        temp_list = list()
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
            self.net_list.extend(self.matchSubdomain(self.domain, respContent))
            self.lock.release()
            re_ip = re.search(r'\d+.\d+.\d+:?\d?', i[0])  # 1.1.1.1:80 -> 1.1.1:80  http://1.1.1.1:80 -> 1.1.1.1:80
            if re_ip:
                self.net_list.append(i[0])  # 只要是ip就添加到列表中
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
                self.net_list.append(i[0])  # 只要是域名就添加到列表中

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

            temp_list.append(ip_info)
        self.lock.acquire()
        self.web_ip_lists_fofa.extend(temp_list)
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
                self.net_list.append(i['ip_str'])  # 只要是ip就添加到列表中

                try:
                    hostname = i['hostnames'][0]
                    self.net_list.append(hostname)
                except KeyError as e:
                    hostname = ''

                #  获取其中的所有主键
                try:
                    product = i['product']
                except KeyError as e:
                    product = ''

                try:
                    title, service, RespOfTitleAndServer = self.getTitleAndService(hostname, i['port'])
                    self.lock.acquire()
                    self.net_list.extend(self.matchSubdomain(self.domain, RespOfTitleAndServer))
                    self.lock.release()
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

        except IOError as e:
            print('[-] curl shodan.io error. {}'.format(e.args))

        except KeyError as e:
            # KeyError 为 API无效
            print("API次数已经用完 | API无效！")
            return
        self.lock.acquire()
        self.web_ip_lists_shodan.extend(temp_list)
        self.lock.release()

    # SSL证书查询函数
    def fofaSSLSpider(self):
        pass

        # FOFA的线程处理函数

    def quakeSSLSpider(self):
        pass

    def shodanSSLSpider(self):
        pass

    # Favicon查询函数
    def fofaFaviconSpider(self):
        pass

    def quakeFaviconSpider(self):
        pass

    def shodanFaviconSpider(self):
        pass

    # 域名爬取的fofa处理函数
    def spider(self):
        fafaIpList = self.fofaDomainSpider()
        quakeIpList = self.quakeDomainSpider()
        shodanIpList = self.shodanDomainSpider()

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

    # fofa引擎的探测搜索ip段和域名
    def fofa_ip_search(self, networksegment):
        # print(NetworkSegment)
        for page in range(1, config.fofa_page):  # 这里自定义页数
            self.thread_list.append(Thread(target=self.test01, args=(networksegment, page)))

        for i in self.thread_list:
            i.start()

        for i in self.thread_list:
            i.join()

    # shodan引擎的探测搜索ip段和域名
    def shadon_ip_search(self, networksegment):
        # print(NetworkSegment)
        for page in range(1, config.shodan_page):
            self.thread_list.append(Thread(target=self.test02, args=(networksegment, page)))

        for i in self.thread_list:
            i.start()

        for i in self.thread_list:
            i.join()

    # main start
    def main(self):
        logging.info("Net Spider Start")
        self.spider()
        return list(set(self.net_list))


if __name__ == '__main__':
    start = time.time()
    NetSpider('zjhu.edu.cn').main()
    print(time.time() - start)
