
port_rules = {
    'FTP': '21',
    'SSH': '22',
    'Telnet': '23',
    'SMTP': '25',
    'DNS': '53',
    'DHCP': '68',
    'HTTP': '80',
    'TFTP': '69',
    'HTTP': '8080',
    'POP3': '995',
    'NetBIOS': '139',
    'IMAP': '143',
    'HTTPS': '443',
    'SNMP': '161',
    'LDAP': '489',
    'SMB': '445',
    'SMTPS': '465',
    'Linux R RPE': '512',
    'Linux R RLT': '513',
    'Linux R cmd': '514',
    'Rsync': '873',
    'IMAPS': '993',
    'Proxy': '1080',
    'JavaRMI': '1099',
    'Lotus': '1352',
    'MSSQL': '1433',
    'MSSQL': '1434',
    'Oracle': '1521',
    'PPTP': '1723',
    'cPanel': '2082',
    'CPanel': '2083',
    'Zookeeper': '2181',
    'Docker': '2375',
    'Zebra': '2604',
    'MySQL': '3306',
    'Kangle': '3312',
    'RDP': '3389',
    'SVN': '3690',
    'Rundeck': '4440',
    'GlassFish': '4848',
    'PostgreSql': '5432',
    'PcAnywhere': '5632',
    'VNC': '5900',
    'CouchDB': '5984',
    'varnish': '6082',
    'Redis': '6379',
    'Weblogic': '9001',
    'Kloxo': '7778',
    'Zabbix': '8069',
    'RouterOS': '8291',
    'Elasticsearch': '9200',
    'Elasticsearch': '9300',
    'Zabbix': '10050',
    'Zabbix': '10051',
    'Memcached': '11211',
    'MongoDB': '27017',
    'MongoDB': '28017',
    'Hadoop': '50070'
}

'''功能：根据port识别服务'''
def Common_getPortService(port):
    print("==============")
    print(port)
    print("==============")
    for k, v in port_rules.items():
        print(111)
        if v == port:
            print(11111111)
            return k
    return 'Unknown'

print(Common_getPortService(22))