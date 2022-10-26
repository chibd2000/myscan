# coding=utf-8
# author: uniodesec

class Constants:
    magic = 44269  # 0xaced
    version = 5  # 0005

    SC_WRITE_METHOD = int.from_bytes(b'\x01', 'big')
    SC_BLOCK_DATA = int.from_bytes(b'\x08', 'big')
    SC_SERIALIZABLE = int.from_bytes(b'\x02', 'big')
    SC_EXTERNALIZABLE = int.from_bytes(b'\x04', 'big')
    TC_BASE = b'\x70'

    # Null object reference.
    TC_NULL = b'\x70'

    # Reference to an object already written into the bin.
    TC_REFERENCE = b'\x71'

    # new Class Descriptor.
    TC_CLASSDESC = b'\x72'

    # new Object.
    TC_OBJECT = b'\x73'

    # new String.
    TC_STRING = b'\x74'

    # new Array.
    TC_ARRAY = b'\x75'

    # Reference to Class.
    TC_CLASS = b'\x76'

    # Block of optional data. Byte following tag indicates number of bytes in this block data.
    TC_BLOCKDATA = b'\x77'

    # End of optional block data blocks for an object.
    TC_ENDBLOCKDATA = b'\x78'

    # Reset bin context. All handles written into bin are reset.
    TC_RESET = b'\x79'

    # long Block data. The long following the tag indicates the number of bytes in this block data.
    TC_BLOCKDATALONG = b'\x7A'

    # Exception during write.
    TC_EXCEPTION = b'\x7B'

    # Long string.
    TC_LONGSTRING = b'\x7C'

    # new Proxy Class Descriptor.
    TC_PROXYCLASSDESC = b'\x7D'

    # new Enum constant.
    TC_ENUM = b'\x7E'

    # Last tag value.
    TC_MAX = b'\x7E'

    # First wire handle to be assigned.
    baseWireHandle = int.from_bytes(b'\x7e\x00\x00', 'big')
