# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-06 20:48

class Mydict(dict):
    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError("unable to access item '{}'".format(item))


if __name__ == '__main__':
    a = Mydict()
    a['a'] = 1
    print(a['b'])
