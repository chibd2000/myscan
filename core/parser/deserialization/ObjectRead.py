# coding=utf-8
# author: uniodesec

from core.parser.deserialization import Constants
from core.parser.deserialization.Exceptions import InvalidHeaderException, InvalidTypeCodeException
from core.parser.deserialization.JavaMetaClass import JavaProxyClass, JavaClassDesc, JavaEndBlock, JavaObject, JavaField, JavaString, JavaClass, \
    JavaBLockData, JavaArray, JavaEnum, JavaException, JavaLongBLockData
from core.parser.deserialization.ObjectIO import ObjectIO


class ObjectRead:
    def __init__(self, stream):
        self.bin = ObjectIO(stream)
        self.handles = []
        self.readStreamHeader()

    def newHandles(self, __object__):
        self.handles.append(__object__)
        return len(self.handles) - 1 + Constants.baseWireHandle

    def readStreamHeader(self):
        magic = self.bin.readUnsignedShort()
        version = self.bin.readUnsignedShort()
        if magic != Constants.magic or version != Constants.version:
            raise InvalidHeaderException(magic, version)

    def readClassDescriptor(self):
        """
        读取非动态代理类的结构, 已经将读取到的classdesc添加到handle中
        :return:
        """
        tc = self.bin.peekByte()
        if tc == Constants.TC_CLASSDESC:
            javaClass = self.__readClassDesc__()
        elif tc == Constants.TC_REFERENCE:
            javaClass = self.readHandle()
        else:
            raise InvalidTypeCodeException(tc)
        return javaClass

    def readProxyClassDescriptor(self):
        """
        读取动态代理类的结构
        # TODO: 此处可能有问题，需要进一步检查
        :return:
        """
        tc = self.bin.readByte()
        if tc != Constants.TC_PROXYCLASSDESC:
            raise InvalidTypeCodeException(tc)
        interfaceCount = self.bin.readInt()
        print(f"Interface count {interfaceCount}")
        interfaces = []
        for i in range(interfaceCount):
            interfaceName = self.bin.readString()
            interfaces.append(interfaceName)
            print("--------------")
            print(interfaceName)
        javaProxyClass = JavaProxyClass(interfaces)
        handle = self.newHandles(javaProxyClass)
        print(f"TC_PROXYCLASSDESC new handle from {hex(handle)}")
        self.readClassAnnotations(javaProxyClass)
        javaProxyClass.superJavaClass = self.readSuperClassDesc()
        return javaProxyClass

    def __readClassDesc__(self):
        tc = self.bin.readByte()
        if tc != Constants.TC_CLASSDESC:
            raise InvalidTypeCodeException(tc)
        # read Class name from bin
        className = self.bin.readString()
        suid = self.bin.readLong()
        flags = self.bin.readByte()
        flags = int.from_bytes(flags, 'big')
        numFields = self.bin.readUnsignedShort()
        externalizable = flags & Constants.SC_EXTERNALIZABLE != 0
        sflag = flags & Constants.SC_SERIALIZABLE != 0
        hasWriteObjectData = flags & Constants.SC_WRITE_METHOD != 0
        hasBlockExternalData = flags & Constants.SC_BLOCK_DATA != 0
        if externalizable and sflag:
            print("serializable and externalizable flags conflict")

        print(f"className {className}")
        print(f"suid {suid}")
        print(f"number of fields {numFields}")
        classDesc = JavaClassDesc(className, suid, flags)
        classDesc.hasWriteObjectData = hasWriteObjectData
        classDesc.hasBlockExternalData = hasBlockExternalData
        handle = self.newHandles(classDesc)
        print(f"TC_CLASSDESC new handle from {hex(handle)} className {className}")
        fields = []
        for i in range(numFields):
            tcode = self.bin.readByte()
            fname = self.bin.readString()
            if tcode == b'L' or tcode == b'[':
                signature = self.readTypeString()
            else:
                signature = tcode.decode()
            fields.append({'name': fname, 'signature': signature})
            print(f"name {fname} signature {signature}")
            classDesc.fields = fields
        self.readClassAnnotations(classDesc)
        superjavaClass = self.readSuperClassDesc()
        classDesc.superJavaClass = superjavaClass
        return classDesc

    def readClassAnnotations(self, classDesc):
        """
        读取类的附加信息
        """
        print(f"ClassAnnotations start ")
        while True:
            __obj__ = self.readContent()
            classDesc.classAnnotations.append(__obj__)
            if isinstance(__obj__, JavaEndBlock):
                break

        print(f"ClassAnnotations end ")

    def readSuperClassDesc(self):
        """
        读取父类的的class信息，一直到父类为空，类似于链表。java不支持多继承
        :return:
        """
        tc = self.bin.peekByte()
        print(f"Super Class start")
        if tc != Constants.TC_NULL:
            superJavaClass = self.readClassDescriptor()
        else:
            self.bin.readByte()
            superJavaClass = None
        print(f"Super Class End")
        return superJavaClass

    def readObject(self):
        tc = self.bin.readByte()
        if tc != Constants.TC_OBJECT:
            raise InvalidTypeCodeException(tc)
        tc = self.bin.peekByte()
        javaClass = None
        if tc == Constants.TC_CLASSDESC:
            javaClass = self.readClassDescriptor()
        elif tc == Constants.TC_NULL:
            return self.readNull()
        elif tc == Constants.TC_REFERENCE:
            javaClass = self.readHandle()
        elif tc == Constants.TC_PROXYCLASSDESC:
            javaClass = self.readProxyClassDescriptor()
        else:
            raise InvalidTypeCodeException(tc)

        javaObject = JavaObject(javaClass)
        handle = self.newHandles(javaObject)
        print(f"readObject new handle from {hex(handle)}")
        self.readClassData(javaObject)
        return javaObject

    def readClassData(self, javaObject):
        """
        读取对象的值，先读取父类的值，再读取子类的值
        :return:
        """
        superClass = javaObject.javaClass
        superClassList = []
        while superClass:
            superClassList.append(superClass)
            superClass = superClass.superJavaClass

        while superClassList:
            classDesc = superClassList.pop()
            fields = classDesc.fields
            currentField = []
            for field in fields:
                signature = field['signature']
                value = self.readFieldValue(signature)
                javaField = JavaField(field['name'], signature, value)
                currentField.append(javaField)
            javaObject.fields.append(currentField)
            if classDesc.hasWriteObjectData:
                self.readObjectAnnotations(javaObject)

    def readHandle(self):
        """
        反序列化中是不会出现两个一摸一样的值，第二个值一般都是引用
        :return:
        """
        self.bin.readByte()
        handle = self.bin.readInt()
        print(hex(handle))
        handle = handle - Constants.baseWireHandle
        return self.handles[handle]

    def readTypeString(self):
        tc = self.bin.peekByte()
        if tc == Constants.TC_NULL:
            return self.readNull()
        elif tc == Constants.TC_REFERENCE:
            return self.readHandle()
        elif tc == Constants.TC_STRING:
            return self.readString()
        elif tc == Constants.TC_LONGSTRING:
            return self.readString()
        else:
            raise InvalidTypeCodeException(tc)

    def readString(self):
        self.bin.readByte()
        string = self.bin.readString()
        javaString = JavaString(string)
        handle = self.newHandles(javaString)
        print(f"readString new handle from {hex(handle)} value {string}")
        return javaString

    def readContent(self):
        tc = self.bin.peekByte()
        if tc == Constants.TC_NULL:
            return self.readNull()
        elif tc == Constants.TC_REFERENCE:
            return self.readHandle()
        elif tc == Constants.TC_CLASS:
            self.bin.readByte()
            clazz = self.readClassDescriptor()
            javaClass = JavaClass(clazz)
            handle = self.newHandles(javaClass)
            print(f"TC_CLASS new handle from {hex(handle)}")
            return javaClass
        elif tc == Constants.TC_CLASSDESC:
            return self.readClassDescriptor()
        elif tc == Constants.TC_PROXYCLASSDESC:
            return self.readProxyClassDescriptor()
        elif tc == Constants.TC_STRING or tc == Constants.TC_LONGSTRING:
            return self.readTypeString()
        elif tc == Constants.TC_ENUM:
            return self.readEnum()
        elif tc == Constants.TC_OBJECT:
            return self.readObject()
        elif tc == Constants.TC_EXCEPTION:
            return self.readException()
        elif tc == Constants.TC_RESET:
            self.readReset()
        elif tc == Constants.TC_ARRAY:
            return self.readArray()
        elif tc == Constants.TC_BLOCKDATA:
            return self.readBlockData()
        elif tc == Constants.TC_BLOCKDATALONG:
            return self.readLongBLockData()
        elif tc == Constants.TC_ENDBLOCKDATA:
            return self.readEndBlock()
        else:
            raise InvalidTypeCodeException(tc)

    def readBlockData(self):
        self.bin.readByte()
        length = int.from_bytes(self.bin.readByte(), 'big')
        data = self.bin.readBytes(length)
        print(data)
        blockData = JavaBLockData(length, data)
        return blockData

    def readEndBlock(self):
        self.bin.readByte()
        endBD = JavaEndBlock()
        return endBD

    def readObjectAnnotations(self, javaObject):
        print("reading readObjectAnnotations")
        while True:
            __obj__ = self.readContent()
            javaObject.objectAnnotation.append(__obj__)
            if isinstance(__obj__, JavaEndBlock):
                break
            # 为了读取8u20 gadget
            if isinstance(__obj__, JavaObject):
                if __obj__.javaClass.name =='sun.reflect.annotation.AnnotationInvocationHandler' and javaObject.javaClass.name == 'java.beans.beancontext.BeanContextSupport':
                    break

    def readNull(self):
        self.bin.readByte()
        return 'null'

    def readArray(self):
        self.bin.readByte()
        tc = self.bin.peekByte()
        javaClass = None
        if tc == Constants.TC_CLASSDESC:
            javaClass = self.readClassDescriptor()
        elif tc == Constants.TC_REFERENCE:
            javaClass = self.readHandle()
        else:
            print("unsupport type")
        size = self.bin.readInt()
        print(javaClass)
        print(f"array size {size}")
        javaarray = JavaArray(size, javaClass)
        handle = self.newHandles(javaarray)
        print(f"TC_ARRAY new handle from {hex(handle)}")
        for i in range(size):
            signature = javaClass.name[1:]
            javaarray.add(self.readFieldValue(signature))
        return javaarray

    def readFieldValue(self, signature: str):
        """
        读取字段的值，根据字段的类型
        """
        if signature.startswith("L") or signature.startswith("["):
            return self.readContent()
        elif signature == 'B':
            return self.bin.readByte()
        elif signature == 'C':
            return self.bin.readChar()
        elif signature == 'D':
            return self.bin.readDouble()
        elif signature == 'F':
            return self.bin.readFloat()
        elif signature == 'I':
            return self.bin.readInt()
        elif signature == 'J':
            return self.bin.readLong()
        elif signature == 'S':
            return self.bin.readShort()
        elif signature == "Z":
            return self.bin.readBoolean()
        else:
            print(f"unsupport signature  {signature}")

    def readEnum(self):
        self.bin.readByte()
        javaClass = self.readClassDescriptor()
        javaEnum = JavaEnum(javaClass)
        handle = self.newHandles(javaEnum)
        print(f"read enum new handle {handle}")
        enumConstantName = self.readContent()
        javaEnum.enumConstantName = enumConstantName
        return javaEnum

    def readReset(self):
        self.bin.readByte()
        self.handles = []

    def readException(self):
        self.bin.readByte()
        self.handles = []
        exception = self.readObject()
        self.handles = []
        javaException = JavaException(exception)
        return javaException

    def readLongBLockData(self):
        self.bin.readByte()
        length = int.from_bytes(self.bin.readBytes(4), 'big')
        data = self.bin.readBytes(length)
        print(data)
        blockData = JavaLongBLockData(length, data)
        return blockData
