# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-01 20:45

from IPy import IP


def getIpSegment(ipList: list):
    ll = []
    for l in ipList:
        l = l.split(".")
        l[-1] = "0/24"
        joinl = ".".join(l)
        if joinl not in ll:
            ll.append(joinl)
    return ll


gAsnList = [111, 222, 333, 444, 555]
gIpList = ['1.1.1.1', '1.1.1.2', '2.2.2.2', '4.4.4.1', '4.4.4.3', '4.4.4.4', '4.4.4.2']

resList = []
tempIpSegmentList = getIpSegment(gIpList)
for ipSegment in tempIpSegmentList:
    IpSegmentDict = {'ipSegment': ipSegment, 'ip': [], 'num': 0}
    resList.append(IpSegmentDict)
for ip in gIpList:
    for ipSegment in tempIpSegmentList:
        ipList = IP(ipSegment)
        for i in ipList:
            if str(ip) == str(i):
                for j in resList:
                    if j.get('ipSegment') == ipSegment:
                        j['num'] += 1
                        j['ip'].append(ip)
# print(tempIpSegmentList)
# for ip in gIpList:
#     for ipSegment in tempIpSegmentList:
#         ipList = IP(ipSegment)
#         for i in ipList:
#             if str(ip) == str(i):
#                 for key, value in resList:
#                     if str(key) == str(ipSegment):
#                         for _ in resList:
#                             if _.get(str(key)):
#                                 _[key] += 1
#                                 _['ip'].append(ip)

#
# for ip in gIpList:
#     for ipSegment in tempIpSegmentList:
#         ipList = IP(ipSegment)
#         for i in ipList:
#             if str(ip) == str(i):
#                 for j in resList:
#                     if j.get(ipSegment):
#                         j[ipSegment] += 1
#                         j['ip'].append(ip)
                    # j[ipSegment] = j[ipSegment]+1
                    # j['ip'].append(ip)





                        #
                        # j[ipSegment] += 1
                        # j['ip'].append(ip)
                    # print(key,value)
                    # if j.get(ipSegment) == :
                    #     j[ipSegment] += 1
                    #     j['ip'].append(ip)
print(resList)
