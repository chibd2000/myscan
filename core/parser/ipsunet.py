# coding=utf-8
# @Author   : zpchcbd HG team
# @blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2021-11-26 15:46

"""
write in 2021.11.26 15.46 @zpchcbd

实现的目的：
1、filterCDN方法添加(为后面的portscan模块节省时间，如果的cdn网段的ip进行端口扫描的话是无意义的)
"""


def ip_to_binary(ip):
    ip_num = ip.split('.')
    x = 0

    """
    IP地址是点分十进制，例如：192.168.1.33，共32bit
    第1节（192）向前移24位，第2节（168）向前移16位
    第3节（1）向迁移8位，第4节（33）不动
    然后进行或运算，得出数据
    """
    for i in range(len(ip_num)):
        num = int(ip_num[i]) << (24 - i * 8)
        x = x | num

    binary_str = str(bin(x).replace('0b', ''))
    return binary_str


def mask_to_binary(mask):
    """
    两种情况的处理
    1、/24
    2、255.255.255.0
    """
    mask_list = str(mask).split('.')

    # 子网掩码有两种表现形式，例如：/24或255.255.255.0
    if len(mask_list) == 1:
        # 生成一个32个元素均是0的列表
        binary32 = []
        for i in range(32):
            binary32.append('0')

        # 多少位子网掩码就是连续多少个1
        for i in range(int(mask)):
            binary32[i] = '1'

        binary = ''.join(binary32)

    # 输入的子网掩码是255.255.255.0这种点分十进制格式
    elif len(mask_list) == 4:
        binary = ip_to_binary(mask)

    return binary


# 判断IP地址是否属于这个网段
def ip_in_subnet(ip, subnet):
    try:
        subnet_list = subnet.split('/')
        networt_add = subnet_list[0]
        network_mask = subnet_list[1]

        # 原来的得出的二进制数据类型是str，转换数据类型
        ip_num = int(ip_to_binary(ip), 2)
        subnet_num = int(ip_to_binary(networt_add), 2)
        mask_bin = int(mask_to_binary(network_mask), 2)

        # IP和掩码与运算后比较
        if (ip_num & mask_bin) == (subnet_num & mask_bin):
            return True
        else:
            return False
    except Exception:
        return False


# ip段识别
def get_ip_segment(ip_list):
    ll = []
    for l in ip_list:
        l = l.split(".")
        l[-1] = "0/24"
        joinl = ".".join(l)
        if joinl not in ll:
            ll.append(joinl)
    return ll


"""
test func 
not use 
"""


def test(ipList, ipSegmentList):
    filter_ip_list = []
    for ip in ipList:
        flag = True
        for ipSegment in FILTER_CDN_IPSEGMENT_LIST:
            if ip_in_subnet(ip, ipSegment):
                flag = False
                break
        if flag:
            filter_ip_list.append(ip)
    temp_ip_segment_list = get_ip_segment(filter_ip_list)
    for ipSegment in temp_ip_segment_list:
        ipSegmentList.append({'ipSegment': ipSegment, 'ip': [], 'num': 0})

    for ip in filter_ip_list:
        for index, ipSegment in enumerate(ipSegmentList):
            if ip_in_subnet(ip, ipSegment['ipSegment']):
                ipSegmentList[index]['num'] += 1
                ipSegmentList[index]['ip'].append(ip)


if __name__ == '__main__':
    from core.constant import FILTER_CDN_IPSEGMENT_LIST

    ip_list = ['39.108.197.102', '8.135.120.84', '119.23.87.120', '1.180.12.242', '121.37.230.188', '39.108.8.160',
               '47.107.127.116', '42.193.65.239', '120.78.170.186', '13.250.76.48', '47.107.25.230', '47.107.193.22']
    print(len(ip_list))
    seg = []
    test(ip_list, seg)
    print(len(seg))
    print(seg)
