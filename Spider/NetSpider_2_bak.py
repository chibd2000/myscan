# coding=utf-8

from Spider.BaseSpider import *
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Thread
import base64
import shodan


class NetSpider(Spider):
    def __init__(self, target, task_list):
        super().__init__()
        self.headers = {
            "Connection": "keep-alive",
            "Cookie": "_fofapro_ars_session=6bb0f9103ad346581b5a26b50ef386bd",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36 ',
        }

        self.target = target

        self.scan_domain_lists = task_list
        self.scan_ip_lists = list()
        self.web_domain_lists = list()
        self.web_ip_lists = list()

        self.thread_list = list()
        self.lock = Lock()

    '''保存文件'''
    def write_file(self, web_lists, target, page):
        # 写文件的时候，这里需要加锁防止覆盖
        '''
    [
        [{'spider': 'fofa', 'subdomain': '123.123.123.124:22', 'title': '', 'ip': '123.123.123.124', 'domain': '', 'port': '22', 'web_service': '', 'port_service': 'SSH', 'search_keyword': 'ip="123.123.123.123/24" && port="22"'}, {'spider': 'fofa', 'subdomain': '123.123.123.123:22', 'title': '', 'ip': '123.123.123.123', 'domain': '', 'port': '22', 'web_service': '', 'port_service': 'SSH', 'search_keyword': 'ip="123.123.123.123/24" && port="22"'}],
        [{'spider': 'fofa', 'subdomain': 'https://www.5890788.com', 'title': '', 'ip': '123.123.123.123', 'domain': '5890788.com', 'port': '443', 'web_service': '', 'port_service': 'HTTPS', 'search_keyword': 'ip="123.123.123.123/24" && port="443"'}]
    ]
        '''

        workbook = openpyxl.load_workbook("C:\\Users\\dell\\Desktop\\自己练手脚本\\MyFrameWork\\" + str(target) + ".xlsx")
        worksheet = workbook.worksheets[page]  # 打开的是证书的sheet
        self.lock.acquire()
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
        workbook.save("C:\\Users\\dell\\Desktop\\自己练手脚本\\MyFrameWork\\" + str(target) + ".xlsx")
        workbook.close()
        self.lock.release()


    def test01(self, ip_, page):
        url = "https://fofa.so/api/v1/search/all?email=admin@chinacycc.com&key" \
              "=69a2b36c3a68bbe6832686b4d257d3a3&qbase64=" + base64.b64encode(
            ip_.encode()).decode() + '&page=' + str(page)

        print(url)
        '''
        https://fofa.so/api/v1/search/all?email=admin@chinacycc.com&key=69a2b36c3a68bbe6832686b4d257d3a3&qbase64=xxxxx&page=1
        '''
        resp = requests.get(url=url, headers=self.headers)

        json_data = resp.json()

        if not json_data['results']:
            print("无数据爬取 break!!!")
            exit(0)

        for i in json_data['results']:
            title, service = self.get_titleAndservice(i[0], i[2])  # 请求标题与服务

            re_ip = re.match(r'\d+.\d+.\d+:?\d?', i[0])  # 1.1.1.1:80 -> 1.1.1:80
            if re_ip:
                self.scan_ip_lists.append(i[0])  # 只要是ip就添加到列表中
                domain = ''
            else:
                domain = i[0].split('.', 1)[1]
                self.scan_domain_lists.append(i[0])  # 只要是域名就添加到列表中

            # if re.match(r'\d+.\d+.\d+', i[0].split('.', 1)[1]):
            #     domain = ''
            # else:
            #     domain = i[0].split('.', 1)[1]

            # if self.target in domain:
            #     self.task_queue.put(domain)

            ip_info = {
                'spider': 'fofa',
                'subdomain': i[0],
                'title': title,
                'ip': i[1],
                'domain': domain,
                'port': i[2],
                'web_service': service,
                'port_service': Common_getPortService(i[2]),
                'search_keyword': ip_
            }

            print(ip_info)

            self.web_ip_lists.append(ip_info)

    def web_search(self, target):
        ip_list = list()  # 存储存在的ip网段 /24
        domain_word = 'domain="%s"' % target

        for page in range(1, 2):
            url = "https://fofa.so/api/v1/search/all?email=admin@chinacycc.com&key" \
                  "=69a2b36c3a68bbe6832686b4d257d3a3&qbase64=" + base64.b64encode(
                domain_word.encode()).decode() + '&page=' + str(page)

            print(url)

            resp = requests.get(url=url, headers=self.headers)

            json_data = resp.json()
            if not json_data['results']:
                print("无数据爬取 break!!!")
                break
            print(json_data)
            for i in json_data['results']:

                title, service = self.get_titleAndservice(i[0], i[2])

                re_ip = re.match(r'\d+.\d+.\d+:?\d?', i[0])  # 1.1.1.1:80 -> 1.1.1:80
                if re_ip:
                    self.scan_ip_lists.append(i[0])  # 只要是ip就添加到列表中
                    domain = ''
                else:
                    domain = i[0].split('.', 1)[1]
                    self.scan_domain_lists.append(i[0])  # 只要是域名就添加到列表中

                ip_list.append(i[1])
                sub_domain = i[0]
                if 'http' in i[0]:
                    sub_domain = i[0].split('//')[1]  # https://www.baidu.com => www.baidu.com

                sub_domain_info = {
                    'spider': 'fofa',
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
        self.write_file(self.web_domain_lists, target, 3)

        # ip_net = ip_list  #  临时保存需要爬取的C段

        # 开始对ip的网段进行爬取
        print("=" * 30)
        print(ip_list)
        print("=" * 30)
        ip_list = Common_getIpSegment(ip_list)  # 对ip进行过滤
        fofa_ip_list = ['ip="%s/24"' % i for i in ip_list]
        shodan_ip_list = ['net:"%s/24"' % i for i in ip_list]
        fofa_ip_list.extend(shodan_ip_list)
        web_ip_all_list = list()

        p = ThreadPoolExecutor(25) # 因为是C段，所以这里使用线程池来进行分配
        for i in fofa_ip_list:
            if 'ip=' in i:
                obj = p.submit(self.fofa_ip_search, i) # 这里只查了ip
            # else:
                #obj = p.submit(self.shadon_ip_search, i) # 这里查了hostname net
            else:
                pass

            web_ip_all_list.append(obj)  # 把返回的结果保存在空的列表中

        p.shutdown()  # 所有计划运行完毕，关闭结束线程池
        print("=" * 30)
        print(web_ip_all_list)
        print("=" * 30)
        results = [obj.result() for obj in web_ip_all_list]

        for result in results:
            '''def write_file(self, web_lists, target):'''
            result = Common_getUniqueList(result)
            self.write_file(result, target, 3)

        # return ip_net

    def fofa_ip_search(self, ip_):
        web_ip_lists = list()
        for page in range(1, 3):
            self.thread_list.append(Thread(target=self.test01, args=(ip_, page)))
            # url = "https://fofa.so/api/v1/search/all?email=admin@chinacycc.com&key" \
            #       "=69a2b36c3a68bbe6832686b4d257d3a3&qbase64=" + base64.b64encode(
            #     ip_.encode()).decode() + '&page=' + str(page)
            #
            # print(url)
            # '''
            # https://fofa.so/api/v1/search/all?email=admin@chinacycc.com&key=69a2b36c3a68bbe6832686b4d257d3a3&qbase64=xxxxx&page=1
            # '''
            # resp = requests.get(url=url, headers=self.headers)
            #
            # json_data = resp.json()
            #
            # if not json_data['results']:
            #     print("无数据爬取 break!!!")
            #     break
            #
            # for i in json_data['results']:
            #     title, service = self.get_titleAndservice(i[0], i[2])  # 请求标题与服务
            #
            #     re_ip = re.match(r'\d+.\d+.\d+:?\d?', i[0])  # 1.1.1.1:80 -> 1.1.1:80
            #     if re_ip:
            #         self.scan_ip_lists.append(i[0])  # 只要是ip就添加到列表中
            #         domain = ''
            #     else:
            #         domain = i[0].split('.', 1)[1]
            #         self.scan_domain_lists.append(i[0])  # 只要是域名就添加到列表中
            #
            #     # if re.match(r'\d+.\d+.\d+', i[0].split('.', 1)[1]):
            #     #     domain = ''
            #     # else:
            #     #     domain = i[0].split('.', 1)[1]
            #
            #         # if self.target in domain:
            #         #     self.task_queue.put(domain)
            #
            #     ip_info = {
            #         'spider': 'fofa',
            #         'subdomain': i[0],
            #         'title': title,
            #         'ip': i[1],
            #         'domain': domain,
            #         'port': i[2],
            #         'web_service': service,
            #         'port_service': Common_getPortService(i[2]),
            #         'search_keyword': ip_
            #     }
            #
            #     print(ip_info)
            #
            #     web_ip_lists.append(ip_info)
        for i in self.thread_list:
            i.start()
        for i in self.thread_list:
            i.join()

        return web_ip_lists

    # shodan引擎的探测搜索ip段和域名
    def shadon_ip_search(self, ip_):
        web_ip_list = list()

        for page in range(1, 10):
            url = "https://api.shodan.io/shodan/host/search?key=rFfYZfaZ9ZIzrAm8tYGtXDkNN4fBvUIa&query="+ip_+"&minify=true&page="+str(page)
            resp = requests.get(url=url, headers=self.headers)
        return web_ip_list

    '''主函数'''
    def main(self):
        print("fofa开始解析...")
        self.web_search(self.target)
        print(list(set(self.scan_ip_lists)))
        print(list(set(self.scan_domain_lists)))
        print("fofa结束解析...")


if '__main__' == __name__:
    NetSpider(1).main('nbcc.cn')
