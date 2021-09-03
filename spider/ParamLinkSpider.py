# coding=utf-8
# @Author   : HengGe's team
# @Time     : 2021-08-25 13:28
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from spider.BaseSpider import *


class ParamsLinkSpider():
    @staticmethod
    def getLinks(url):
        # 1、https://www.yamibuy.com/cn/brand.php?id=566
        # 2、http://www.labothery-tea.cn/chanpin/2018-07-12/4.html

        # if 'gov.cn' in self.url:
        #     return 0
        #     pass
        # http://www.baidu.com/ -> www.baidu.com/ -> www.baidu.com -> baidu.com
        domain = url.split('//')[1].strip('/').replace('www.', '')
        result = []
        id_links = []
        html_links = []
        result_links = {}
        html_links_s = []
        result_links['title'] = '网址标题获取失败'
        idid = []
        htht = []
        try:
            rxww = requests.get(url, headers=self.headers, verify=False, timeout=self.reqTimeout)
            soup = BeautifulSoup(rxww.content, 'html.parser', from_encoding='iso-8859-1')

            try:
                encoding = requests.utils.get_encodings_from_content(rxww.text)[0]
                res = rxww.content.decode(encoding, 'replace')
                title_pattern = '<title>(.*?)</title>'
                title = re.search(title_pattern, res, re.S | re.I)
                result_links['title'] = str(title.group(1))
            except:
                pass

            if result_links['title'] == '' or result_links['title'] == None:
                result_links['title'] = '网址标题获取失败'

            links = soup.findAll('a')
            for link in links:  # 判断是不是一个新的网站
                _url = link.get('href')
                res = re.search('(javascript|:;|#|%)', str(_url))
                res1 = re.search(
                    '.(jpg|png|bmp|mp3|wma|wmv|gz|zip|rar|iso|pdf|txt)', str(_url))
                if res == None and res1 == None:
                    result.append(str(_url))  # 是的话 那么添加到result列表中
                else:
                    pass
            # print(result)
            # time.sleep(50)
            if result != []:
                rst = list(set(result))
                for rurl in rst:  # 再进行二次判断是不是子域名 这次的判断有三种情况
                    if '//' in rurl and 'http' in rurl and domain in rurl:
                        # http // domain 都在
                        # https://www.yamibuy.com/cn/search.php?tags=163
                        # http://news.hnu.edu.cn/zhyw/2017-11-11/19605.html
                        if '?' in rurl and '=' in rurl:
                            # result_links.append(rurl)
                            id_links.append(rurl.strip())
                        if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
                            if '?' not in rurl:
                                # result_links.append(rurl)
                                html_links.append(rurl.strip())
                    # //wmw.dbw.cn/system/2018/09/25/001298805.shtml
                    if 'http' not in rurl and domain in rurl:
                        # http 不在    domain 在
                        if '?' in rurl and '=' in rurl:
                            id_links.append('http://' + rurl.lstrip('/').strip())
                        if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
                            if '?' not in rurl:
                                html_links.append(
                                    'http://' + rurl.lstrip('/').strip())

                    # /chanpin/2018-07-12/3.html"
                    if 'http' not in rurl and domain not in rurl:
                        # http 不在  domain 不在
                        if '?' in rurl and '=' in rurl:
                            id_links.append(
                                'http://' + domain.strip() + '/' + rurl.strip().lstrip('/'))
                        if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
                            if '?' not in rurl:
                                html_links.append(
                                    'http://' + domain.strip() + '/' + rurl.strip().lstrip('/'))

                # print(html_links)
                # print(id_links)
                # time.sleep(50)

                for x1 in html_links:  # 对于爬取到的后缀是html等等参数链接进行二次处理 是否能够访问
                    try:
                        rx1 = requests.get(url=x1, headers=self.headers, timeout=self.reqTimeout)
                        if rx1.status_code == 200:
                            htht.append(x1)
                    except Exception as e:
                        print('error, {}'.format(e.args))

                for x2 in id_links:  # 平常的id?=1 这种参数进行二次处理 是否能够访问
                    try:
                        rx2 = requests.get(url=x2, headers=self.headers, timeout=self.reqTimeout)
                        if rx2.status_code == 200:
                            if rx2.url.find('=') > 0:
                                idid.append(rx2.url)
                    except Exception as e:
                        print('error, {}'.format(e.args))

                hthtx = []
                ididx = []
                dic_1 = []
                dic_2 = []
                dic_3 = []
                dic_4 = []
                for i in htht:
                    path = urlparse(i).path
                    if path.count('/') == 1:
                        dic_1.append(i)
                    if path.count('/') == 2:
                        dic_2.append(i)
                    if path.count('/') == 3:
                        dic_3.append(i)
                    if path.count('/') > 3:
                        dic_4.append(i)
                if dic_1:
                    hthtx.append(random.choice(dic_1))
                if dic_2:
                    hthtx.append(random.choice(dic_2))
                if dic_3:
                    hthtx.append(random.choice(dic_3))
                if dic_4:
                    hthtx.append(random.choice(dic_4))
                dic_11 = []
                dic_21 = []
                dic_31 = []
                dic_41 = []
                for i in idid:
                    path = urlparse(i).path
                    if path.count('/') == 1:
                        dic_11.append(i)
                    if path.count('/') == 2:
                        dic_21.append(i)
                    if path.count('/') == 3:
                        dic_31.append(i)
                    if path.count('/') > 3:
                        dic_41.append(i)
                if dic_11:
                    ididx.append(random.choice(dic_11))
                if dic_21:
                    ididx.append(random.choice(dic_21))
                if dic_31:
                    ididx.append(random.choice(dic_31))
                if dic_41:
                    ididx.append(random.choice(dic_41))

                if hthtx == []:
                    pass
                else:
                    result_links['html_links'] = hthtx

                if ididx == []:
                    pass
                else:
                    result_links['id_links'] = ididx

            with open('test.txt', 'a+', encoding='utf-8')as a:
                if ididx:
                    for i in ididx:
                        a.write(i + '\n')
                if hthtx:
                    for u in hthtx:
                        a.write(u.replace('.htm', '*.htm').replace('.shtm', '*.shtm') + '\n')

            if result_links == {}:
                return None
            else:
                return result_links

        except Exception as e:
            print('error, {}'.format(e.args))
            pass
        return None


if __name__ == '__main__':
    pass
