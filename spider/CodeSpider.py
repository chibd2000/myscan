# coding=utf-8
# author：ske
# python3
import requests
import re
import chardet
from optparse import OptionParser

requests.packages.urllib3.disable_warnings()
from termcolor import cprint


# 1、 循环一个列表中的子域名 每个子域名都进行递归请求
# 2、 每个子域名在进行递归请求之前先判断：是否该域名已经存在A列表中 如果存在则continue
# 3、 继续如果该域名请求返回为匹配到的子域名规则为空 同样也加入到A列表中
# 4、 以此类推 一直到子域名循环递归请求结束

class CrwalSpider:
    def __init__(self, url):
        self.url = url  # 主站
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36"}
        urlsplit = url.split(".")
        self.domain = url if len(urlsplit) == 2 else urlsplit[-2] + "." + urlsplit[-1]  # 域名
        self.SubDomainList = [url]  # 子域名列表
        # 域名匹配规则
        self.domain_patten = re.compile('https?:\/\/[^"/]+?\.{url}'.format(url=urlsplit[-2] + "\." + urlsplit[-1]))
        print(self.domain_patten)
        # 标题匹配规则
        self.title_patten = re.compile('<title>(.*)?</title>')
        self.url_except = []  # 存放请求异常的url
        self.result = []

    # 开始从主站开始爬取
    def start(self):
        self.getSubDomain(self.url, 0)

        # 对异常的url再重新跑一遍
        print('异常：{}'.format(self.url_except))
        url_excepts = self.url_except[:]  # 创建一个新的列表。内容是url_except列表里的url
        for url_except in url_excepts:
            self.getSubDomain(url_except, 0)

        # 打印所有结果
        for ret in self.result:
            print(ret)

    # 获取域名列表
    def getSubDomain(self, url, layer):
        layer += 1

        # 有些https站请求可以会抛出异常，这里捕获，并将url放入url_except列表里。
        try:
            res = requests.get(url, headers=self.headers, timeout=5, verify=False)
        except Exception as e:
            self.url_except.append(url)  # 将请求异常的url放入url_except列表里。
            res = None

        try:
            self.code_title(url, res)
            subdomains = list(set(re.findall(self.domain_patten, res.text)))  # 子域名列表,去重结果
            print(subdomains)
            # 遍历匹配到的所有子域名
            for subdomain in subdomains:
                print('第【{}】层 : {}'.format(layer, subdomain))
                # 如果这个子域名之前没添加进列表里
                if subdomain not in self.SubDomainList:
                    self.SubDomainList.append(subdomain)
                    self.getSubDomain(subdomain, layer)
                else:
                    print('{}已经在列表里'.format(subdomain))

        except Exception as e:
            pass

    # 获取域名的标题和状态码
    def code_title(self, url, res):
        result = {}
        code = res.status_code
        try:
            cont = res.content
            # 获取网页的编码格式
            charset = chardet.detect(cont)['encoding']
            # 对各种编码情况进行判断
            html_doc = cont.decode(charset)
        except Exception as e:
            html_doc = res.text

        try:
            # self.title_patten = re.compile('<title>(.*)?</title>')
            title = re.search(self.title_patten, html_doc).group(1)
            result['url'], result['code'], result['title'] = url, code, title
        except Exception as e:
            result['url'], result['code'], result['title'] = url, code, 'None'
        finally:
            cprint(result, 'red')
            self.result.append(str(result))
            self.save(str(result))

    def save(self, result):
        with open('{}.txt'.format(self.domain), 'at', encoding='utf-8') as f:
            f.writelines(result + '\n')


if __name__ == "__main__":
    usage = r'usage : %prog python3 getSubDomain.py -u http://www.qq.com'
    parse = OptionParser(usage=usage)
    parse.add_option('-u', '--url', dest='url', type='string', help='url or domain')
    options, args = parse.parse_args()
    CrwalSpider(options.url).start()

    # url = 'http://www.taobao.com'
    # getSubDomain(url).start()