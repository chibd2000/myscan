# coding=utf-8

from Spider.BaseSpider import *
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from Config import config
import base64

# 这里需要配合fofa搜集到的网段来进行shodan的爬取，所以两个模块一起写，处理函数还是分开写了 test01 test02，为了增加效率 每页的爬取都用一个线程
class NetSpider(Spider):
    def __init__(self, target):
        super().__init__()
        self.source = 'fofa shodan spider'
        self.headers = {
            "Connection": "keep-alive",
            "Cookie": "_fofapro_ars_session=6bb0f9103ad346581b5a26b50ef386bd",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36 ',
        }
        self.target = target
        self.net_list = list() # 存放所有爬取到的url
        self.web_domain_lists = list()  # 存放域名信息的的列表
        self.web_ip_lists_shodan = list()  # shodan存放ip信息的列表
        self.web_ip_lists_fofa = list()  # fofa存放ip信息的列表
        self.thread_list = list()
        self.fofa_api = config.fofa_api
        self.shodan_api = config.shodan_api

    '''保存文件'''
    def write_file(self, web_lists, target, page):
        '''

        :param web_lists:
        :param target:
        :param page:
        :return:
        '''
        # 写文件的时候，这里多线程安全所以需要加锁防止覆盖，拼接格式如下
        '''
    [
        [{'spider': 'fofa', 'subdomain': '123.123.123.124:22', 'title': '', 'ip': '123.123.123.124', 'domain': '', 'port': '22', 'web_service': '', 'port_service': 'SSH', 'search_keyword': 'ip="123.123.123.123/24" && port="22"'}, 
         {'spider': 'fofa', 'subdomain': '123.123.123.123:22', 'title': '', 'ip': '123.123.123.123', 'domain': '', 'port': '22', 'web_service': '', 'port_service': 'SSH', 'search_keyword': 'ip="123.123.123.123/24" && port="22"'}],
        [{'spider': 'fofa', 'subdomain': 'https://www.5890788.com', 'title': '', 'ip': '123.123.123.123', 'domain': '5890788.com', 'port': '443', 'web_service': '', 'port_service': 'HTTPS', 'search_keyword': 'ip="123.123.123.123/24" && port="443"'}]
    ]
        '''
        workbook = openpyxl.load_workbook(os.getcwd() + os.path.sep + str(target) + ".xlsx")
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
        workbook.save(os.getcwd() + os.path.sep + str(target) + ".xlsx")
        workbook.close()

    # fofa的线程处理函数
    def test01(self, NetworkSegment, page):
        '''
        :param ip_:
        :param page:
        :return:
        '''

        logging.info("Fofa Spider page {}".format(page))
        temp_list = list()
        url = "https://fofa.so/api/v1/search/all?email=admin@chinacycc.com&key=" + str(self.fofa_api) + "&qbase64=" + base64.b64encode(
            NetworkSegment.encode()).decode() + '&page=' + str(page)

        #  print(url)
        '''
        https://fofa.so/api/v1/search/all?email=admin@chinacycc.com&key= + str(self.fofa_api) + &qbase64=xxxxx&page=1
        '''
        resp = requests.get(url=url, headers=self.headers)

        json_data = resp.json()

        if not json_data['results']:
            print("{} {} {} 无数据爬取 break!!!".format('fofa', NetworkSegment, page))
            exit(0)

        for i in json_data['results']:
            title, service, respoftitleandserver = self.get_titleAndservice(i[0], i[2])  # 请求标题与服务
            self.lock.acquire()
            self.net_list.extend(self.matchSubdomain(self.target, respoftitleandserver))
            self.lock.release()
            re_ip = re.search(r'\d+.\d+.\d+:?\d?', i[0])  # 1.1.1.1:80 -> 1.1.1:80  http://1.1.1.1:80 -> 1.1.1.1:80
            if re_ip:
                self.net_list.append(i[0])  # 只要是ip就添加到列表中
                domain = ''
            else:
                # 要探测的目标正好是在其中，比如 self.target = 'nbcc.cn'，那么子域名也就是nbcc.cn，如果目标是nbcc.edu.cn 那么直接就取 不跟下面的edu gov继续判断，那么就是直接略过

                #print("原始爬取的网址为：" + str(i[0]))
                if self.target in i[0]:
                    domain = self.target
                    # print("1-处理过后的网址为：" + str(domain))
                # 特殊的edu gov的域名处理
                elif 'edu' in i[0] or 'gov' in i[0]:
                    domain_temp = i[0].split('.')
                    if len(domain_temp) >= 4:
                        domain = ".".join(domain_temp[len(domain_temp)-3:])
                        # print("2-处理过后的网址为：" + str(domain))
                    else:
                        domain = i[0]
                        # print("3-处理过后的网址为：" + str(domain))
                else:
                    domain_temp = i[0].split('.')
                    if len(domain_temp) >= 3:
                        domain = ".".join(domain_temp[len(domain_temp)-2:])
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
                'port_service': Common_getPortService(i[2]),
                'search_keyword': NetworkSegment
            }

            # print(ip_info)

            temp_list.append(ip_info)
        self.lock.acquire()
        self.web_ip_lists_fofa.extend(temp_list)
        self.lock.release()

    # shodan的线程处理函数
    def test02(self, NetworkSegment, page):
        logging.info("Shodan Spider page {}".format(page))

        temp_list = list()
        url = "https://api.shodan.io/shodan/host/search?key=" + self.shodan_api + "&query=" + NetworkSegment + "&minify=true&page=" + str(page)
        resp = requests.get(url=url, headers=self.headers)
        json_data = resp.json()

        try:
            if not json_data['matches']:
                print("{} {} {} 无数据爬取 break!!!".format('shodan', NetworkSegment, page))
                exit(0)
        except:
            print("API查询次数用尽/网络延迟高 SHODAN")

        for i in json_data['matches']:
            self.net_list.append(i['ip_str'])  # 只要是ip就添加到列表中

            try:
                hostname = i['hostnames'][0]
                self.net_list.append(hostname)
            except:
                hostname = ''

            #  获取其中的所有主键
            try:
                product = i['product']
            except:
                product = ''

            try:
                title, service, respoftitleandserver = self.get_titleAndservice(hostname, i['port'])
                self.lock.acquire()
                self.net_list.extend(self.matchSubdomain(self.target, respoftitleandserver))
                self.lock.release()
                # title = i['http']['title']
            except:
                title = ''

            try:
                hostname = i['hostnames'][0]
            except:
                hostname = ''

            try:
                domains = ','.join(i['domains'])
            except:
                domains = ''


            ip_info = {
                'spider': 'Shodan',
                'subdomain': hostname,
                'title': title,# !!!!
                'ip': i['ip_str'],
                'domain': domains,
                'port': i['port'],
                'web_service': product, #!!!!
                'port_service': Common_getPortService(i['port']),
                'search_keyword': NetworkSegment
            }

            # print(ip_info)
            temp_list.append(ip_info)
        self.lock.acquire()
        self.web_ip_lists_shodan.extend(temp_list)
        self.lock.release()

    # 域名爬取的fofa处理函数
    def spider(self):
        ip_list = list()  # 存储存在的ip网段 /24
        domain_word = 'domain="%s"' % self.target

        for page in range(1, 3):
            url = "https://fofa.so/api/v1/search/all?email=admin@chinacycc.com&key=" + str(self.fofa_api) + "&qbase64=" + base64.b64encode(
                domain_word.encode()).decode() + '&page=' + str(page)

            # print(url)

            resp = requests.get(url=url, headers=self.headers)

            json_data = resp.json()
            if not json_data['results']:
                print("{} {} 无数据爬取 break!!!".format(domain_word, page))
                break
            # print(json_data)
            for i in json_data['results']:

                title, service, respoftitleandserver = self.get_titleAndservice(i[0], i[2])
                self.lock.acquire()
                self.net_list.extend(self.matchSubdomain(self.target, respoftitleandserver))
                self.lock.release()
                re_ip = re.match(r'\d+.\d+.\d+:?\d?', i[0])  # 1.1.1.1:80 -> 1.1.1:80
                if re_ip:
                    self.net_list.append(i[0])  # 只要是ip就添加到列表中
                    domain = ''
                else:
                    if self.target in i[0]:
                        domain = self.target
                    else:
                        domain = ''

                    self.net_list.append(i[0])  # 只要是域名就添加到列表中

                ip_list.append(i[1])
                sub_domain = i[0]
                if 'http' in i[0]:
                    sub_domain = i[0].split('//')[1]  # https://www.baidu.com => www.baidu.com

                sub_domain_info = {
                    'spider': 'FOFA',
                    'subdomain': sub_domain,
                    'title': title,
                    'ip': i[1],
                    'domain': domain,
                    'port': i[2],
                    'web_service': service,
                    'port_service': Common_getPortService(i[2]),
                    'search_keyword': domain_word
                }

                print(sub_domain_info)

                self.web_domain_lists.append(sub_domain_info)

        self.web_domain_lists = Common_getUniqueList(self.web_domain_lists)

        self.lock.acquire()
        self.write_file(self.web_domain_lists, self.target, 3)
        self.lock.release()

        # ip_net = ip_list  #  临时保存需要爬取的C段

        # 开始对ip的网段进行爬取
        ip_list = Common_getIpSegment(ip_list)  # 对ip进行过滤
        print("=" * 30)
        print(ip_list)
        print("=" * 30)
        fofa_ip_list = ['ip="%s/24"' % i for i in ip_list]
        shodan_ip_list = ['net:"%s/24"' % i for i in ip_list]
        fofa_ip_list.extend(shodan_ip_list)

        p = ThreadPoolExecutor(25)  # 因为是C段，所以这里使用线程池来进行分配
        for i in fofa_ip_list:
            if 'ip=' in i:
                obj = p.submit(self.fofa_ip_search, i)  # 这里只查 ip="
            else:
                pass
                # obj = p.submit(self.shadon_ip_search, i) # 这里只查 net="

        p.shutdown()  # 所有计划运行完毕，关闭结束线程池

        self.write_file(self.web_ip_lists_fofa, self.target, 3)
        self.write_file(self.web_ip_lists_shodan, self.target, 4)


        # results = [obj.result() for obj in web_ip_all_list]
        # for result in results:
        #     '''def write_file(self, web_lists, target):'''
        #     result = Common_getUniqueList(result)
        #     self.write_file(result, target, 3)
        # return ip_net

    # fofa引擎的探测搜索ip段和域名
    def fofa_ip_search(self, NetworkSegment):
        # print(NetworkSegment)
        for page in range(1, 2): # 这里自定义页数
            self.thread_list.append(Thread(target=self.test01, args=(NetworkSegment, page)))

        for i in self.thread_list:
            i.start()
        for i in self.thread_list:
            i.join()

    # shodan引擎的探测搜索ip段和域名
    def shadon_ip_search(self, NetworkSegment):
        # print(NetworkSegment)
        for page in range(1, 5):
            self.thread_list.append(Thread(target=self.test02, args=(NetworkSegment, page)))

        for i in self.thread_list:
            i.start()
        for i in self.thread_list:
            i.join()

    '''主函数'''
    def main(self):
        logging.info("Net Spider Start")
        self.spider()
        return list(set(self.net_list))


if '__main__' == __name__:
    NetSpider('nbcc.cn').main()
