# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 18:05
# bypass CloudFlare

import cfscrape
# # pip install cloudscraper -U
scraper = cfscrape.create_scraper()  # returns a CloudScraper instance

proxies = {
    'http': 'http://103.219.112.178:8080',
    'https': 'https://103.219.112.178:8080'
}

# scraper = cloudscraper.CloudScraper()  # CloudScraper inherits from requests.Session
# print(scraper.get('https://dns.bufferover.run/dns?q=.zjhu.edu.cn').text)  # => "<!DOCTYPE html><html><head>..."

print(scraper.get('https://dns.bufferover.run/dns?q=.zjhu.edu.cn', proxies=proxies).text)
# => "<!DOCTYPE html><html><head>..."
