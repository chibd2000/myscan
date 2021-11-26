# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-06 20:48


class Mydict(dict):
    """
    prepare for exploitModule. write in 2021.11.27 0.16 @zpchcbd

    write the class's reason:
    1. 我发现默认的dict的key无法进行存储自定义的类对象
    2. 在于攻击类中的CmsScan，我需要实现同类型多模块的节省时间利用
    3. 在该自定义的dict中我可以实现存在Script对象
    """
    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError("unable to access item '{}'".format(item))


if __name__ == '__main__':
    a = Mydict()
    a['a'] = 1
    print(a['b'])
