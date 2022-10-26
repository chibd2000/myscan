# coding=utf-8
# @Author   : zpchcbd HG team
# @blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2021-11-25 0:18

from tldextract import extract
from urllib.parse import urlparse


class UrlParser:
    """
    解析url相关格式信息
    write in 2021.11.24 14.26 @zpchcbd
    """

    def __init__(self, url):
        self._extract_result = extract(url) # ExtractResult(subdomain='', domain='1.1.1.1', suffix='')
        self._parse_result = urlparse(url) # ParseResult(scheme='http', netloc='1.1.1.1', path='', params='', query='', fragment='')

    @property
    def subdomain(self):
        return f'{self._extract_result.subdomain}.{self._extract_result.domain}.{self._extract_result.suffix}' if self._extract_result.subdomain and self._extract_result.domain and self._extract_result.suffix else ''

    @property
    def rootdomain(self):
        return f'{self._extract_result.domain}.{self._extract_result.suffix}' if self._extract_result.domain and self._extract_result.suffix else ''

    @property
    def scheme(self):
        return f'{self._parse_result.scheme}://'

    @property
    def url_no_param(self):
        return f'{self._parse_result.scheme}://{self._parse_result.netloc}{self._parse_result.path}'

    @property
    def url_no_path(self):
        return f'{self._parse_result.scheme}://{self._parse_result.netloc}'

    @property
    def extract_result(self):
        return self._extract_result

    @property
    def parse_result(self):
        return self._parse_result


if __name__ == '__main__':
    t = UrlParser('http://baidu.com:8080/?a=1')
    print(t.extract_result)
    print(t.parse_result)
    # print(t.subdomain)
    print(t.rootdomain)
    # print(t.scheme)
    # print(t.url_no_param)
    # print(t.url_no_path)
