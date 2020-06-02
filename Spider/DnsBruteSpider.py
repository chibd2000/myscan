# coding=utf-8
from Spider.BaseSpider import *
import subprocess
import os
import re

abs_path = os.getcwd() + os.path.sep

'''他山之石subDomainsdBrute模块'''
class subDomaindBrute(Spider):
    def __init__(self, target):
        super().__init__()
        self.source = 'DomainBrute'
        self.target = target
        self.dnsbrute_list = list()

    def spider(self):
        cmd = 'python2 ' + abs_path + 'subDomainsBrute' + os.path.sep + 'subDomainsBrute.py ' + str(self.target) + ' -i'  # --full'
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        result = res.stdout.read().decode()

        fina_res = re.split(r'\s+', result, flags=re.S)
        for i in fina_res:
            if fina_res[fina_res.index(i)] == '':
                fina_res.remove(i)

        res.terminate()
        self.dnsbrute_list = fina_res

    def write_file(self, web_lists, target, page):
        pass

    # 调用口
    def main(self):
        logging.info("DnsBrute Spider Start")
        self.spider()
        return self.dnsbrute_list


if __name__ == '__main__':
    pass
