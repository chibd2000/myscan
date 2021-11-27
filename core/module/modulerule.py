# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-10-22 19:28

# 减少同类型多模块加载的时间消耗所写的类
class ModuleRule:
    """
    存储格式应该为
    remainModuleList = [{"seeyon"}]
    """
    # JAVA
    Jboss = []  # JBOSS
    # OA系列
    Weaver = []  # 泛微系列OA
    Landray = []  # 蓝凌系列OA
    Seeyon = []  # 致远系列OA
    Tongda = []  # 通达系列OA
    Yonyou = []  # 用友系列OA

    # 第三方服务系统
    Zabbix = []  # ZABBIX
    Couchdb = []  # Couchdb

    # 邮件系统
    Coremail = []
