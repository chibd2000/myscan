
import requests

def shodon_ip_search(ip_):

    url = "https://api.shodan.io/shodan/host/search?key=rFfYZfaZ9ZIzrAm8tYGtXDkNN4fBvUIa&query=" + ip_ + "&minify=true&page=1"
    resp = requests.get(url=url)
    json_data = resp.json()
    for i in json_data['matches']:
        web_list = list()
        ip_info = {
            'spider': 'shodan',
            'subdomain': i['hostnames'],
            'title': i['http']['title'],
            'ip': i['ip_str'],
            'domain': i['domains'],
            'port': i['port'],
        }
        print(ip_info)
        web_list.append(ip_info)

shodon_ip_search('net:"219.222.181.0/24"')
