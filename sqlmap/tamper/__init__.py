# coding:utf-8

# import os,sys,time
#
#
# if os.path.exists('Langzi_Api'):
#     try:
#         lis = (os.path.join(os.getcwd() + '\Langzi_Api\GET_IP\masscan'))
#         os.popen('start' + lis + '\masscan.exe --version')
#         if 'CPU' in os.read():
#             pass
#     except Exception,e:
#         print e
#         print unicode('需要安装wincap.exe依赖')
#         time.sleep(30)
#
#         print lis
#         if lis in os.environ['PATH']:
#             pass
#         else:
#             os.environ['PATH'] = os.environ['PATH']+ ';' + lis
#             print os.environ['PATH']
#     except Exception,e:
#         print e

# if 'Langzi_Api' in os.environ['PATH']:
#     pass
# else:
#     lis = sys.prefix + '\Lib\site-packages\Langzi_Api\GET_IP;'
#     os.environ['PATH'] = os.environ['PATH'] + ';' + lis
