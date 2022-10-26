# coding=utf-8
# author: uniodesec

reference = []


class JavaEndBlock:
    def __eq__(self, other):
        return isinstance(other, JavaEndBlock)


"""
两种block的区别在于size的大小，一个为byte，一个为int
"""


class JavaBLockData:
    def __init__(self, size, data):
        self.size = size
        self.data = data

    def __eq__(self, other):
        if not isinstance(other, JavaBLockData):
            return False
        return self.size == other.size and self.data == other.data


class JavaLongBLockData:
    def __init__(self, size, data):
        self.size = size
        self.data = data

    def __eq__(self, other):
        if not isinstance(other, JavaLongBLockData):
            return False
        return self.size == other.size and self.data == other.data


class JavaClassDesc:
    def __init__(self, name, suid, flags):
        self.name = name
        self.suid = suid
        self.flags = flags
        self.superJavaClass = None
        self.fields = []
        self.classAnnotations = []
        self.hasWriteObjectData = False

    def __eq__(self, other):
        if not isinstance(other, JavaClassDesc):
            return False
        return other.name == self.name

    def __str__(self):
        return f"javaclass {self.name}"


class JavaClass:
    def __init__(self, javaclassDesc):
        self.javaclassDesc = javaclassDesc

    def __eq__(self, other):
        if not isinstance(other, JavaClass):
            return False
        return self.javaclassDesc == other.javaclassDesc


class JavaProxyClass:
    def __init__(self, interfaces):
        self.interfaces = interfaces
        self.classAnnotations = []
        self.superJavaClass = None
        self.fields = []
        self.hasWriteObjectData = False
        self.name = "Dynamic proxy"

    def __eq__(self, other):
        if not isinstance(other, JavaProxyClass):
            return False
        for i in zip(self.interfaces, other.interfaces):
            if i[0] != i[1]:
                return False
        return self.superJavaClass == other.superJavaClass


class JavaException:
    def __init__(self, exception):
        self.exception = exception

    def __eq__(self, other):
        if not isinstance(other, JavaException):
            return False
        return self.exception == other.exception


class JavaArray:
    def __init__(self, length, signature):
        self.signature = signature
        self.length = length
        self.list = []

    def add(self, __obj__):
        self.list.append(__obj__)

    def __eq__(self, other):
        if not isinstance(other, JavaArray):
            return False
        if self.length != other.length:
            return False
        for i in zip(self.list, other.list):
            if i[0] != i[1]:
                return False
        return True


class JavaEnum:
    def __init__(self, javaClass):
        self.javaClass = javaClass
        self.enumConstantName = None

    def __eq__(self, other):
        if not isinstance(other, JavaEnum):
            return False
        return other.javaClass == self.javaClass and self.enumConstantName == other.enumConstantName


class JavaString:
    def __init__(self, string):
        self.string = string

    def startswith(self, string):
        return self.string.startswith(string)

    def __str__(self):
        return self.string

    def __eq__(self, other):
        if not isinstance(other, JavaString):
            return False
        return other.string == self.string


class JavaObject:
    def __init__(self, javaClass):
        self.javaClass = javaClass
        # fields 保存类的字段，队列数据结构。父类在最前，子类在最后
        self.fields = []
        self.objectAnnotation = []

    def __str__(self):
        return f"className {self.javaClass.name}\t extend {self.javaClass.superJavaClass}"

    def __eq__(self, other):
        if not isinstance(other, JavaObject):
            return False
        if id(other) == id(self):
            return True
        if other.javaClass != self.javaClass:
            return False
        if len(other.fields) != len(self.fields):
            return False
        else:
            if id(self) in reference:
                return True
            else:
                reference.append(id(self))
            for i in zip(self.fields, other.fields):
                for j in zip(*i):
                    if j[0].value == self and j[1].value == other:
                        continue
                    if j[0] != j[1]:
                        reference.pop()
                        return False
        if len(other.objectAnnotation) != len(self.objectAnnotation):
            reference.pop()
            return False
        else:
            for i in zip(other.objectAnnotation, self.objectAnnotation):
                if i[0] != i[1]:
                    reference.pop()
                    return False
        reference.pop()
        return True


class JavaField:
    def __init__(self, name, signature, value):
        self.fieldName = name
        self.signature = signature
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, JavaField):
            return False
        return other.signature == self.signature and other.value == self.value and other.fieldName == self.fieldName
