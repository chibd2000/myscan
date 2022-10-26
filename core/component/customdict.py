# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-06 20:48

class AttributeDict(dict):
    def __init__(self, temp_dict=None):
        if temp_dict is None:
            temp_dict = {}
        super().__init__(temp_dict)

    def __setattr__(self, key, value):
        super().__setitem__(key, value)

    def __getattr__(self, key):
        return self.__getitem__(key)


class WriteDict(dict):
    def __init__(self, temp_dict, init_fields):
        super().__init__(temp_dict)
        self.init_fields = init_fields

    def __getitem__(self, __k):
        _key = self.init_fields[__k]
        return super().__getitem__(_key)


class ModuleDict(dict):
    """
    prepare for exploitModule. write in 2021.11.27 0.16 @zpchcbd

    write the class's reason:
    1. 我发现默认的dict的key无法进行存储自定义的类对象
    2. 在于攻击类中的CmsScan，我需要实现同类型多模块的节省时间利用
    3. 在该自定义的dict中我可以实现存在Script对象
    """
    pass


if __name__ == '__main__':
    INIT_FIELDS = ['a', 'b', 'c']
    mydict = WriteDict({"a": 1, "b": 2, "c": 3}, INIT_FIELDS)
    print(mydict[0])
