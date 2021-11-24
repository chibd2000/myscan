# coding=utf-8
# @Author   : zpchcbd HG team
# @blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2021-11-22 12:59

"""封装一个日志类，想要实现的是文件和控制台都可以记录相关信息"""
import logging


class Logger:
    def __init__(self, path, clevel=logging.DEBUG, Flevel=logging.DEBUG):
        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)  # 设置logger级别
        self.formatter = logging.Formatter('[%(levelname)s]%(asctime)s %(message)s')

        sh = logging.StreamHandler()
        sh.setFormatter(self.formatter)
        sh.setLevel(clevel)  # 设置处理器的Level

        fh = logging.FileHandler(path)
        fh.setFormatter(self.formatter)
        fh.setLevel(Flevel)  # 设置处理器的Level

        self.logger.addHandler(sh)
        self.logger.addHandler(fh)

    def getLogger(self):
        return self.logger

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


if __name__ == '__main__':
    mLogger = Logger('./logs.txt', logging.DEBUG, logging.DEBUG)
    # mLogger.debug('HengGe test...., , debug')
    # mLogger.info('HengGe test...., , info')
    # mLogger.warn('HengGe test....,  warning')
    # mLogger.error('HengGe test....,  error')
    # mLogger.cri('HengGe test...., , critical')
    asnList = [{'service': 'http', 'ip': ['47.110.217.169:8080', '47.113.23.213:8080', '58.251.27.73:8080', '113.98.59.166:8080', '63.221.140.244:8080', '47.254.137.137:8080', '58.251.27.73:9000']}, {'service': 'bgp', 'ip': ['58.60.230.102:179']}, {'service': 'https-alt', 'ip': ['47.110.217.169:8443', '47.96.196.50:8443']}, {'service': 'osiris', 'ip': ['103.27.119.242:541']}, {'service': 'cisco-sccp', 'ip': ['58.60.230.103:2000']}, {'service': 'redis', 'ip': ['127.0.0.1:6377']}, {'service': 'smtp', 'ip': ['202.103.147.169:25', '202.103.147.161:25', '63.217.80.70:25', '202.103.147.172:25']}, {'service': 'ssl/http', 'ip': ['47.52.122.123:8443']}, {'service': 'http-proxy', 'ip': ['222.134.66.173:8080', '222.134.66.177:8080']}]
    ip = [{'ipSegment': '183.232.187.0/24', 'ip': ['183.232.187.210', '183.232.187.201', '183.232.187.197'], 'num': 3}, {'ipSegment': '218.2.178.0/24', 'ip': ['218.2.178.29', '218.2.178.22', '218.2.178.23', '218.2.178.21', '218.2.178.15', '218.2.178.14', '218.2.178.27', '218.2.178.32'], 'num': 8}]
    mLogger.info('111111')
    mLogger.info('111111')
    mLogger.info('111111')
    mLogger.info('222222')
    mLogger.info('222222')