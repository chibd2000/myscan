# coding=utf-8

from core.data import path_dict, GlobalVariableManager, config_dict
from core.setting import LOG_PATH, OUTPUT_PATH, SPIDER_PATH, EXPLOIT_PATH, DICT_PATH, CONFIG_PATH, SPIDER_THIRD_PATH
from argparse import ArgumentParser
from core.utils.tools import read_yaml_to_dict
import os


def getVersion():
    return 'Myscan Tool\'s version is 3.0 - HengGe'


def parser_init():
    parser = ArgumentParser(prog='MyScan', description='the tool is beneficial to search and attack')
    parser.add_argument('-u', '--url', type=str, help='a url. for example: -u hengge.com')
    parser.add_argument('-d', '--domain', type=str, help='target domain. for example: -d hengge.com')
    parser.add_argument('-c', '--company', type=str, help='target company. for example: -cn 横戈安全有限公司')
    parser.add_argument('-i', '--ips', type=str, help='target ip. for example: -i 192.168.1.1-192.168.1.127,192.168.3.1-192.168.3.255 | 192.168.1.0/24,192.168.3.0/24 | 192.168.1.1,192.168.1.2')
    parser.add_argument('-p', '--port', type=str, default='top100', help='default scan top100, for example: -p top100')
    parser.add_argument('-m', '--module', type=str, help='load exploit module，for example: -m exploit.a.b.c')
    parser.add_argument('-s', '--show', action='store_true', help='show exploit module，example: -s')
    parser.add_argument('-f', '--find', type=str, help='find module exploit module，for example: -f thinkphp')
    parser.add_argument('-uf', '--url_file', type=str, help='scan in target url file, for example: -uf url.txt')
    parser.add_argument('-if', '--ip_file', type=str, help='scan port in target ip file, for example: -ipf ip.txt')
    parser.add_argument('-fs', '--fofa', type=str, help=r'fofa scan title. for example: -fs "domain=\"hengge.com\""')
    parser.add_argument('-ws', '--websearch', action='store_true', help='for example: -ws')
    parser.add_argument('-cs', '--webscan', action='store_true', help='for web scan, for example: -cs')
    parser.add_argument('-fn', '--webfunc', default='attack', help='for web scan, for example: -fn attack')
    parser.add_argument('-ss', '--servicescan', action='store_true', help='for service scan, for example ssh,ftp,mysql,mssql,redis,rsync...')
    parser.add_argument('-k', '--ksub', action='store_true', help='for example: -k')
    parser.add_argument('-x', '--proxy', type=str, default='http://127.0.0.1:7890', help='default 127.0.0.1:7890, for example: -x http://127.0.0.1:7890')
    parser.add_argument('-t', '--threads', type=int, default=500, help='default 500, for example -t 500')
    parser.add_argument('-o', '--output', action='store_true', help='default not output, for example: -o')
    parser.add_argument('-dg', '--debug', action='store_true', help='print about debug level information')
    parser.add_argument('-v', '--version', action='version', version=getVersion(), help='display version')
    # return parser.parse_args()
    return parser


def path_init():
    path_dict.LOG_PATH = os.path.join(path_dict.ROOT_PATH, LOG_PATH)
    path_dict.OUTPUT_PATH = os.path.join(path_dict.ROOT_PATH, OUTPUT_PATH)
    path_dict.SPIDER_PATH = os.path.join(path_dict.ROOT_PATH, SPIDER_PATH)
    path_dict.SPIDER_THIRD_PATH = os.path.join(path_dict.ROOT_PATH, SPIDER_THIRD_PATH)
    path_dict.EXPLOIT_PATH = os.path.join(path_dict.ROOT_PATH, EXPLOIT_PATH)
    path_dict.DICT_PATH = os.path.join(path_dict.ROOT_PATH, DICT_PATH)
    path_dict.CONFIG_PATH = os.path.join(path_dict.ROOT_PATH, CONFIG_PATH)


def global_variable_init():
    GlobalVariableManager.init()
    GlobalVariableManager.setValue("remain_module_list", [])


def config_init():
    yaml_config_dict = read_yaml_to_dict(path_dict.CONFIG_PATH)
    for _ in yaml_config_dict:
        config_dict[_] = yaml_config_dict[_]

