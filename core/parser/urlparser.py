# coding=utf-8
# @Author   : zpchcbd HG team
# @blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2021-11-25 0:18

from tldextract import extract
from urllib.parse import urlparse

class urlParser:
    """
    解析url相关格式信息
    write in 2021.11.24 14.26 @zpchcbd
    """
    def __init__(self, url):
        self.extractResult = extract(url)
        self.parseResult = urlparse(url)

    @property
    def rootdomain(self):
        return f'{self.extractResult.subdomain}.{self.extractResult.domain}.{self.extractResult.suffix}' if self.extractResult.subdomain and self.extractResult.domain and self.extractResult.suffix else ''

    @property
    def subdomain(self):
        return f'{self.extractResult.domain}.{self.extractResult.suffix}' if self.extractResult.domain and self.extractResult.suffix else ''

    @property
    def scheme(self):
        return f'{self.parseResult.scheme}://'