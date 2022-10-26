# coding=utf-8
# author: uniodesec

class InvalidHeaderException(Exception):
    def __init__(self, magic, version):
        self.magic = magic
        self.version = version

    def __str__(self):
        print(f"invalid bin header {self.magic:#2x} {self.version:#2x}")


class InvalidTypeCodeException(Exception):
    def __init__(self, errorTc):
        self.tc = errorTc

    def __str__(self):
        return f"invalid type code {int.from_bytes(self.tc, 'big'):#2x}"
