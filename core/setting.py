# coding=utf-8
# @Author   : zpchcbd HG team
# @blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2021-11-23 20:45

CONCURRENCY = 500
# PATH
LOG_PATH = "log/myscan.log"
OUTPUT_PATH = "output/"
DICT_PATH = "dict/information/"
CONFIG_PATH = "conf/myscan.yaml"
SPIDER_PATH = "spider/"
SPIDER_THIRD_PATH = "spider/thirdLib/"
EXPLOIT_PATH = "exploit/scripts/"

# REGEXP
REGEXP_TITLE_STRING = r'<title>(?P<result>[^<]+)</title>'
REGEXP_PARAM_STRING = r''

# SQL Injection
SQL_COMMON_FALG_SIGN = '@@'
SQL_HTML_FLAG_SIGN = '.htm'
SQL_SHTML_FLAG_SIGN = '.shtm'
ERROR_PAYLOAD_XML = 'dict/payload/errors.xml'
BOOL_PAYLOAD_XML = 'dict/payload/bool.xml'
HIGH_RADIO = -1
LOW_RADIO = 2
