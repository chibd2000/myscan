# coding=utf-8
# author: uniodesec

import copy

from core.parser.deserialization.Constants import Constants
from core.parser.deserialization.JavaMetaClass import JavaObject, JavaEndBlock, JavaString, JavaField, JavaBLockData, JavaArray, JavaException, \
    JavaClassDesc, JavaProxyClass, JavaEnum, JavaClass
from core.parser.deserialization.ObjectIO import ObjectIO


class ObjectWrite:
    def __init__(self, stream):
        self.handles = []
        self.stream = ObjectIO(stream)
        self.writeStreamHeader()

    def writeStreamHeader(self):
        self.stream.writeBytes(b'\xac\xed')
        self.stream.writeBytes(b'\x00\x05')

    def writeContent(self, content):
        if isinstance(content, JavaObject):
            self.writeObject(content)
        elif isinstance(content, JavaEndBlock):
            self.writeEndBlock(content)
        elif isinstance(content, JavaString):
            self.writeTypeString(content)
        elif isinstance(content, JavaField):
            self.writeJavaField(content)
        elif isinstance(content, JavaBLockData):
            self.writeJavaBlockData(content)
        elif isinstance(content, JavaArray):
            self.writeJavaArray(content)
        elif isinstance(content, JavaException):
            self.writeJavaException(content)
        elif isinstance(content, JavaClassDesc):
            self.writeJavaClassDesc(content)
        elif isinstance(content, JavaProxyClass):
            self.writeJavaProxyClass(content)
        elif isinstance(content, JavaEnum):
            self.writeEnum(content)
        elif isinstance(content, JavaClass):
            self.writeClass(content)
        elif content == 'null':
            self.stream.writeBytes(Constants.TC_NULL)
        else:
            print(content)

    def writeObject(self, javaObject):
        if javaObject in self.handles:
            self.writeHandle(javaObject)
            return
        self.stream.writeBytes(Constants.TC_OBJECT)
        self.writeClassDesc(javaObject.javaClass)
        self.handles.append(copy.deepcopy(javaObject))

        superClassList = []
        superClass = javaObject.javaClass
        while True:
            if superClass:
                superClassList.append(superClass)
                superClass = superClass.superJavaClass
            else:
                break
        lastWriteObjectAnnotations = 0
        for field in javaObject.fields:
            classDesc = superClassList.pop()
            for i in field:
                self.writeContent(i)
            if classDesc.hasWriteObjectData:
                lastWriteObjectAnnotations = self.writeObjectAnnotations(javaObject.objectAnnotation,
                                                                         lastWriteObjectAnnotations)

    def writeClassDesc(self, javaClass):
        if javaClass in self.handles:
            self.writeHandle(javaClass)
            return
        if isinstance(javaClass, JavaProxyClass):
            return self.writeJavaProxyClass(javaClass)
        self.stream.writeBytes(Constants.TC_CLASSDESC)
        self.stream.writeString(javaClass.name)
        self.stream.writeLong(javaClass.suid)
        self.stream.writeBytes(javaClass.flags.to_bytes(1, 'big'))
        self.stream.writeShort(len(javaClass.fields))
        self.handles.append(javaClass)
        writeTypeString = False
        for i in javaClass.fields:
            if i['signature'].startswith('L') or i['signature'].startswith('['):
                self.stream.writeBytes(i['signature'].string[0].encode())
                writeTypeString = True
            else:
                self.stream.writeBytes(i['signature'].encode())
            self.stream.writeString(i['name'])
            if writeTypeString:
                self.writeTypeString(i['signature'])
        self.writeClassAnnotations(javaClass.classAnnotations)
        if javaClass.superJavaClass is not None:
            self.writeClassDesc(javaClass.superJavaClass)
        else:
            self.stream.writeBytes(Constants.TC_NULL)

    def writeHandle(self, obj):
        handle = self.handles.index(obj)
        print(hex(handle))
        handle = Constants.baseWireHandle + handle
        self.stream.writeBytes(Constants.TC_REFERENCE)
        self.stream.writeInt(handle)

    def writeTypeString(self, javaString):
        if javaString in self.handles:
            self.writeHandle(javaString)
            return
        else:
            self.stream.writeBytes(Constants.TC_STRING)
            self.stream.writeString(javaString.string)
            self.handles.append(javaString)

    def writeClassAnnotations(self, classAnnotations):
        for i in classAnnotations:
            self.writeContent(i)

    def writeEndBlock(self, content):
        self.stream.writeBytes(Constants.TC_ENDBLOCKDATA)

    def writeJavaField(self, content):
        if content.signature.startswith('L') or content.signature.startswith('['):
            self.writeContent(content.value)
        elif content.signature == "B":
            self.stream.writeBytes(content.value)
        elif content.signature == "C":
            self.stream.writeChar(content.value)
        elif content.signature == "D":
            self.stream.writeDouble(content.value)
        elif content.signature == "F":
            self.stream.writeFloat(content.value)
        elif content.signature == 'I':
            self.stream.writeInt(content.value)
        elif content.signature == 'J':
            self.stream.writeLong(content.value)
        elif content.signature == 'S':
            self.stream.writeShort(content.value)
        elif content.signature == 'Z':
            self.stream.writeBoolean(content.value)
        else:
            print("unsupport", content)

    def writeObjectAnnotations(self, objectAnnotation, lastWriteObjectAnnotations):
        while lastWriteObjectAnnotations < len(objectAnnotation):
            self.writeContent(objectAnnotation[lastWriteObjectAnnotations])
            if isinstance(objectAnnotation[lastWriteObjectAnnotations], JavaEndBlock):
                lastWriteObjectAnnotations += 1
                break
            else:
                lastWriteObjectAnnotations += 1

        return lastWriteObjectAnnotations

    def writeJavaBlockData(self, content):
        self.stream.writeBytes(Constants.TC_BLOCKDATA)
        self.stream.writeBytes(content.size.to_bytes(1, 'big'))
        self.stream.writeBytes(content.data)

    def writeJavaArray(self, content):
        if content in self.handles:
            return self.writeHandle(content)
        else:
            self.stream.writeBytes(Constants.TC_ARRAY)
            self.writeClassDesc(content.signature)
            self.stream.writeInt(content.length)
            self.handles.append(content)
            for i in content.list:
                if content.signature.name[1:].startswith("[") or content.signature.name[1:].startswith("L"):
                    self.writeContent(i)
                else:
                    self.writeJavaField(JavaField(None, content.signature.name[1:], i))

    def writeJavaException(self, content):
        self.stream.writeBytes(Constants.TC_EXCEPTION)
        self.handles = []
        self.writeContent(content.exception)
        self.handles = []

    def writeJavaClassDesc(self, content):
        if content in self.handles:
            return self.writeHandle(content)
        else:
            self.stream.writeBytes(Constants.TC_CLASS)
            self.writeClassDesc(content)
            self.handles.append(content)

    def writeJavaProxyClass(self, content):
        if content in self.handles:
            return self.writeHandle(content)
        self.stream.writeBytes(Constants.TC_PROXYCLASSDESC)
        self.stream.writeInt(len(content.interfaces))
        for i in content.interfaces:
            self.stream.writeString(i)
        self.handles.append(content)
        for i in content.classAnnotations:
            self.writeContent(i)
        if content.superJavaClass:
            self.writeClassDesc(content.superJavaClass)
        else:
            self.stream.writeBytes(Constants.TC_NULL)

    def writeEnum(self, content):
        if content in self.handles:
            return self.writeHandle(content)
        self.stream.writeBytes(Constants.TC_ENUM)
        self.writeClassDesc(content.javaClass)
        self.handles.append(content)
        self.writeContent(content.enumConstantName)

    def writeClass(self, content):
        if content in self.handles:
            return self.writeHandle(content)
        self.stream.writeBytes(Constants.TC_CLASS)
        self.writeClassDesc(content.javaclassDesc)
        self.handles.append(content)
