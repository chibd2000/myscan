import requests
import threading


def aaaa(NetworkSegment, page):
    temp_list = list()
    url = "https://api.shodan.io/shodan/host/search?key=rFfYZfaZ9ZIzrAm8tYGtXDkNN4fBvUIa&query=" + NetworkSegment + "&minify=true&page=" + str(page)
    print(url)
    resp = requests.get(url=url)
    json_data = resp.json()
    print(json_data)

    try:
        if not json_data['matches']:
            print("{} {} {} 无数据爬取 break!!!".format('shodan', NetworkSegment, page))
    except:
        print("{} {} {} {} 爬取出现问题请修复BUGBUGBUGBUGBUG!!!".format(url, 'shodan', NetworkSegment, page))

    for i in json_data['matches']:

        try:
            hostname = i['hostnames'][0]
        except:
            hostname = ''

        #  获取其中的所有主键
        try:
            product = i['product']
        except:
            product = ''

        try:
            title = i['http']['title']
        except:
            title = ''

        try:
            hostname = i['hostnames'][0]
        except:
            hostname = ''

        try:
            domains = ','.join(i['domains'])
        except:
            domains = ''

        ip_info = {
            'spider': 'Shodan',
            'subdomain': hostname,
            'title': title,  # !!!!
            'ip': i['ip_str'],
            'domain': domains,
            'port': i['port'],
            'web_service': product,  # !!!!
            'port_service': "12",
            'search_keyword': NetworkSegment
        }

        print(ip_info)


aaaa('net:"183.3.235.0/24"', 3)

print(threading.enumerate())
