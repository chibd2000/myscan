# coding:utf-8

from Spider.BaseSpider import *
from urllib.parse import quote
# 一个搜索引擎爬取的过程：
# 1、爬取链接
# 2、对链接进行访问重定向到真正的网址
# 3、对重定向过后的网站进行保存写入到文件中

# 关于百度的人机验证绕过方法：加上cookie头

abs_path = os.getcwd() + os.path.sep

class BaiduSpider(Spider):
    def __init__(self, target):
        super().__init__()
        self.source = 'BaiduSpider'  #
        self.target = target
        self.header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, compress',
            'Accept-Language': 'en-us;q=0.5,en;q=0.3',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0',
            'Cookie': 'BAIDU_SSP_lcr=http://www.360kuaishi.com/wz_1_2.php; BAIDUID=5A2885F341F0C7A7A026017E2628E957:FG=1; BIDUPSID=5A2885F341F0C7A7A026017E2628E957; PSTM=1570112340; H_WISE_SIDS=137151_126009_114550_136650_135173_136748_136626_114746_134982_136666_136436_137374_120202_136453_136658_136365_137139_132909_136455_136618_131247_132378_131518_118884_118876_118852_118834_118789_107315_132783_136799_136431_133352_137222_136862_136818_137013_137088_129654_136195_132250_125086_135307_133847_132551_134047_129646_131424_134489_136165_110085_135212_127969_136900_131754_131951_136613_135457_128195_136636_134350_136322_136537_136988_100458; BD_UPN=12314753; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDSFRCVID=cVCOJeC624r_BA3uwomCh9mH92KTcDjTH6aoC4muP4k2VOQQ2OpPEG0PJU8g0Ku-NdF0ogKKKgOTHI8F_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tJAHoD-2tK03fP36q4bShnLO-xrQaR38HD7yWCvNBKJcOR5Jj6KB3-Ck3Pntbl3ELK-8WR5xaMJVSPOC3MA--t4OQbDJLl-HLCT83lTRKq6hsq0x0-nYe-bQypoa546ZQKOMahvc5h7xOhI9QlPK5JkgMx6MqpQJQeQ-5KQN3KJmfbL9bT3YjjTXjaDtt5-Hfn3b04bq2R4_JR71q4bohDCShGREex79WDTmWlnnMlR0ftQGWxROy4v-hqOGJfnitIv9-pnsMnvcVMcpX4TAXp0N5JjZKxtq3mkjbPbDfn02OP5P-x8bWt4syP4jKMRnWnciKfA-b4ncjRcTehoM3xI8LNj405OTbIFO0KJzJCFKMKLGjTtKe5PObqOKa4AXMDOQsJOOa6rjDCvo3fOcy4Ldht7mhx7Eb6cthqv8WbPBDtbtDxRvD--g3-7QhPn9LNQK2JruBMbFffQ_bf--QfbQ0hOhqP-jW5Ta3q-5yR7JOpkxbUnxy5KUQRPH-Rv92DQMVU52QqcqEIQHQT3m5-5bbN3ut6IDfK7QW-5eHJoHjJbGq4bohjPzblOeBtQm05bxohn9-JrhoR7uQPQKLPDX3t5wKbj7aN7QLbIbWDFKhI8wejLBD6P0hxry2Dr2aI52B5r_5TrjDnCr0p3rXUI8LNDH-bo7H66nL4oe5J3sbJ6KyJrvKR_NjnO7ttoy-Cjx2nnTblo-hh8xjqPhyxL1Db3yL6vMtg3t3Doq2bRoepvoyPJc3MkPe-jdJJQOBKQB0KnGbUQkeq8CQft20b0EeMtjKjLEtR4q_K_KfCK3fP36q4n2btCyhl-X5-CsKacm2hcH0KLKM-o3LxL55J-ehtb3q4r7fRri-nOg2fb1MRjvLTOV5qO3MN5pWhoIteOjbp5TtUJkSDnTDMRhqfCOQG3yKMniWKv9-pnYfpQrh459XP68bTkA5bjZKxtq3mkjbPbDfn028DKu-n5jHjoLeHuO3f; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; delPer=0; BD_CK_SAM=1; PSINO=3; H_PS_PSSID=1424_31326_21094_31421_31342_30909_30823_31163_31196; sugstore=1; H_PS_645EC=01e2NhJjP9%2FQwhhfAWZNliJkm%2F4VXrQJTSc0Q%2B6FpE5MOiFZEC8rMZjt2IA; BDSVRTM=0'
        }

        self.baidu_list = list() # 存放所有爬取到的url

    ''':保存文件'''
    def write_file(self, web_lists, target, page):
        workbook = openpyxl.load_workbook(abs_path + str(target) + ".xlsx")
        worksheet = workbook.worksheets[page]
        index = 0
        while index < len(web_lists):
            web = list()
            web.append(web_lists[index]['spider'])
            web.append(web_lists[index]['keyword'])
            web.append(web_lists[index]['link'])
            web.append(web_lists[index]['title'])
            worksheet.append(web)
            index += 1
        workbook.save(abs_path + str(target) + ".xlsx")
        workbook.close()

    ''':爬取链接'''
    def keyword(self, kw, page=1):
        kw = quote(kw)
        url = 'https://www.baidu.com/s?wd=%s&pn=%s0' % (kw, page-1)
        req = requests.get(url, headers=self.header)
        res = re.findall(r'<a target="_blank" href="(\S+)" class="c-showurl"', req.content.decode('utf-8'))
        return list(set(res))

    ''':重定向验证'''
    def location(self, baiduLink):
        resp = requests.get(baiduLink, allow_redirects=False)
        location = resp.headers.get('Location')
        self.baidu_list.extend(self.matchSubdomain(self.target, resp.text))
        return location

    def spider(self):
        pages = 10
        web_lists = list()
        words = ['inurl:system', 'inurl:register', 'inurl:login', 'inurl:admin', 'inurl:manage', 'inurl:upload', '后台', '登陆', '系统', 'upload'
                 , 'intitle:"Outlook Web App"', 'intitle:"mail"', 'intitle:"webmail"']
        for word in words:
            for page in range(pages):
                res = map(self.location, self.keyword(word + " site:*." + self.target, page))
                for link in res:
                    title, service, respoftitleandserver = self.get_titleAndservice(link)  # 该函数写在基类中
                    self.lock.acquire()
                    self.baidu_list.extend(self.matchSubdomain(self.target, respoftitleandserver))
                    self.lock.release()
                    self.baidu_list.append(Common_getUrl(link))

                    web_info = {
                        'spider': '百度',
                        'keyword': word,
                        'link': link,
                        'title': title,
                    }

                    web_lists.append(web_info)
        web_lists = Common_getUniqueList(web_lists)
        self.write_file(web_lists, self.target, 0)
        # return list(set(self.baidu_list))

    ''':主函数'''
    def main(self):
        logging.info("BaiduSpider Start")
        self.spider()
        return list(set(self.baidu_list))


if __name__ == '__main__':
    BaiduSpider.main('nbcc.cn')



