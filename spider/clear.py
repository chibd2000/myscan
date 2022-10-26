# coding=utf-8
# @Author   : zpchcbd HG team
# @Blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2022-08-15 21:50
import openpyxl

from core.data import path_dict, gLogger
from spider import BaseSpider
from core.constant import FILTER_CDN_ASN_LIST, FILTER_CDN_IPSEGMENT_LIST
from core.parser.ipsunet import ip_in_subnet, get_ip_segment

class ClearSpider(BaseSpider):
    def __init__(self, domain, name):
        super().__init__()
        self.source = 'ClearSpider'
        self.domain = domain
        self.name = name

    def write_file(self, web_lists, page):
        try:
            workbook = openpyxl.load_workbook(path_dict.ROOT_PATH + str(self.name) + ".xlsx")
            worksheet = workbook.worksheets[page]
            for web_info in web_lists:
                web = []
                for _ in web_info.values():
                    web.append(str(_))
                worksheet.append(web)
            workbook.save(path_dict.ROOT_PATH + str(self.name) + ".xlsx")
            workbook.close()
        except FileNotFoundError:
            gLogger.myscan_warn('if you want to record search and attack information, you need start with -o param.')
        except Exception as e:
            gLogger.myscan_warn('[{}] write_file error, error is {}'.format(self.source, e.__str__()))

    def flush_ip_segment(self, ip_list, ip_segment_list):
        filter_ip_list = []
        for ip in ip_list:
            flag = True
            for ip_segment in FILTER_CDN_IPSEGMENT_LIST:
                if ip_in_subnet(ip, ip_segment):
                    flag = False
                    break
            if flag:
                filter_ip_list.append(ip)

        temp_ip_segment_list = get_ip_segment(filter_ip_list)
        for ip_segment in temp_ip_segment_list:
            ip_segment_list.append({'ipSegment': ip_segment, 'ip': [], 'num': 0})

        for ip in filter_ip_list:
            for index, ip_segment in enumerate(ip_segment_list):
                if ip_in_subnet(ip, ip_segment['ipSegment']):
                    ip_segment_list[index]['num'] += 1
                    ip_segment_list[index]['ip'].append(ip)
        self.write_file(ip_segment_list, 5)
        self._is_continue = False

    def flush_asn(self, asn_list):
        filter_asn_list = []
        for asn in asn_list:
            flag = True
            for filter_asn in FILTER_CDN_ASN_LIST:
                if str(asn) == str(filter_asn):
                    # print(filterAsn)
                    flag = False
                    break
            if flag:
                filter_asn_list.append({'asn': asn})
        self.write_file(filter_asn_list, 6)
        self._is_continue = False

    async def spider(self):
        pass

    async def main(self):
        pass