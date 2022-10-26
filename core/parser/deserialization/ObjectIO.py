# coding=utf-8
# author: uniodesec

from struct import pack, unpack


class ObjectIO:
    def __init__(self, base_stream):
        self.base_stream = base_stream

    def readByte(self) -> bytes:
        return self.base_stream.read(1)

    def peekByte(self) -> bytes:
        return self.base_stream.peek()[:1]

    def readUnsignedShort(self) -> int:
        number = self.readBytes(2)
        number = int.from_bytes(number, 'big')
        return number & 0xFFFF

    def readUnsignedLong(self) -> int:
        number = self.readBytes(8)
        return int.from_bytes(number, 'big', signed=False)

    def readLong(self) -> int:
        number = self.readBytes(8)
        return int.from_bytes(number, 'big', signed=True)

    def readShort(self) -> int:
        number = self.readBytes(2)
        return int.from_bytes(number, 'big')

    def readInt(self) -> int:
        return int.from_bytes(self.readBytes(4), 'big', signed=True)

    def writeInt(self, num):
        self.writeBytes(num.to_bytes(4, 'big', signed=True))

    def readBytes(self, length) -> bytes:
        return self.base_stream.read(length)

    def readString(self) -> str:
        length = self.readUnsignedShort()
        return self.readBytes(length).decode()

    def readFloat(self):
        num = self.readBytes(4)
        # 模拟ieee 754 标准，具体参考https://stackoverflow.com/questions/30124608/convert-unsigned-integer-to-float-in-python
        s = pack('>l', int.from_bytes(num, 'big'))
        return unpack('>f', s)[0]

    def readBoolean(self):
        tc = int.from_bytes(self.readByte(), 'big')
        return True if tc == 0 else False

    def readChar(self):
        tc = self.readBytes(2)
        return tc.decode()

    def readDouble(self):
        tc = self.readBytes(8)
        return unpack('d', tc)[0]

    def writeBytes(self, value):
        self.base_stream.write(value)

    def writeString(self, value):
        length = len(value)
        self.writeShort(length)
        self.writeBytes(value.encode())

    def pack(self, fmt, data):
        return self.writeBytes(pack(fmt, data))

    def unpack(self, fmt, length=1):
        return unpack(fmt, self.readBytes(length))[0]

    def writeShort(self, num):
        self.writeBytes(num.to_bytes(2, "big"))

    def writeLong(self, num):
        self.writeBytes(num.to_bytes(8, "big", signed=True))

    def writeFloat(self, value):
        s = pack('>f', value)
        s = unpack('>l', s)[0]
        self.writeBytes(s.to_bytes(4, 'big'))

    def writeChar(self, value):
        self.writeBytes(value.encode)

    def writeDouble(self, value):
        self.writeBytes(pack('d', value))

    def writeBoolean(self, value):
        value = 0 if value else 1
        self.writeBytes(value.to_bytes(1, 'big'))
