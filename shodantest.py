# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-29 23:17

from shodan import Shodan

api = Shodan('E00hXnOQ4ep8aM309o5QsCH1JyArnAr8')

# Lookup an IP
# ipinfo = api.host('8.8.8.8')
# print(ipinfo)

# Search for websites that have been "hacked"
for banner in api.search_cursor('ssl:"zjhu.edu.cn"'):
    print(banner)
    print("==================")

# Get the total number of industrial control systems services on the Internet
ics_services = api.count('tag:ics')
print('Industrial Control Systems: {}'.format(ics_services['total']))