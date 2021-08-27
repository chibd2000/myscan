import requests
from lxml import etree
import re


def get_beian(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel cai) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
    url = f'https://icp.chinaz.com/home/info?host={url}'

    try:
        response = requests.get(url=url, headers=headers)
        html = etree.HTML(response.text)
        url_href = html.xpath('//div[@class="siteInfo"]/p/text()')
        if not url_href[0].startswith('--'):
            urls = url_href[2:]
            print(urls)
    except Exception as e:
        print(e)


def get_crt(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel cai) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
    url = f'https://crt.sh/?q={url}&output=json'
    try:
        response = requests.get(url=url, headers=headers)
        text = response.json()
        if len(text) > 0:
            for url in text:
                domain = url['name_value'].replace("*.", "")
                print(domain)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    get_crt("geely.com")
