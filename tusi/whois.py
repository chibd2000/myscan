import requests
import re
from lxml import etree
def email_domain(email):
    headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel cai) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
    url=f'https://whois.aizhan.com/reverse-whois/?q={email}&t=email'
    try:
        response=requests.get(url=url,headers=headers)
        html = etree.HTML(response.text)
        url_href=html.xpath('//tbody/tr/td[@class="url domain"]/a/@href')
        # url_title=html.xpath('//tbody/tr/td[@class="owner title"]/a/text()')
        if len(url_href) > 1:
            print(f"当前{email}获取到域名",url_href)
    except  Exception as e:
        print(e)
def name_domain(name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel cai) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
    url = f'https://whois.aizhan.com/reverse-whois/?q={name}&t=registrant'
    try:
        response = requests.get(url=url, headers=headers)
        html = etree.HTML(response.text)
        url_href = html.xpath('//tbody/tr/td[@class="url domain"]/a/@href')
        if len(url_href) > 1:
            print(f"当前{name}获取到域名", url_href)
        else:
            print(f"当前{name}没有获取到域名",url_href)
    except  Exception as e:
        print(e)
if __name__ == '__main__':
    pass
    # with open('name.txt','r') as f:
        # for u in f:
            # name_domain(u.strip())
    # email_domain('1xxx@qq.com')
    # name_domain('集团有限公司')
