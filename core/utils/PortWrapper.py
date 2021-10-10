# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-07 20:54

# for port wrapper，用来包装端口的，默认最低扫描合并TOP100端口加上fofa/quake/shodan，配合异步端口探测
class PortWrapper(object):

    # parse Command
    def parseCommand(self):
        # 第一种解析 80,90,9090 这种形式的
        pass

        # 第二种解析 80-9090 或者 加上逗号类型的，比如80-9090,70-8080 这种形式的
        pass

    # generate ports
    def generatePorts(self):
        pass
