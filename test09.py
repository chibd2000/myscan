
import requests

def aaaa(ip_):

    url = "https://api.shodan.io/shodan/host/search?key=rFfYZfaZ9ZIzrAm8tYGtXDkNN4fBvUIa&query=" + ip_ + "&minify=true&page=1"
    resp = requests.get(url=url)
    json_data = resp.json()
    for i in json_data['matches']:

        keys = i.keys()
        try:
            for key in keys:
                if 'product' == key:
                    product = i["product"]
                else:
                    product = ''
        except:
            product = ''

        try:
            keys = i['http'].keys()

            for key in keys:
                if 'title' == key:
                    title = i['http']['title']
                else:
                    title = ''
        except:
            title = ''
        print(product, title)

aaaa('net:"219.148.158.0/24"')
