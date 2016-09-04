#!/usr/bin/python3

import struct

class XNBFormatException(Exception):
    def __init__(self,description=''):
        self.description=description

def readUInt32(inputstream):
    data=inputstream.read(4)
    data=struct.unpack('I',data)[0]
    return data

def readInt32(inputstream):
    data=inputstream.read(4)
    data=struct.unpack('i',data)[0]
    return data

def read7BitEncodedInt(inputstream):
    result=0
    bitsRead=0
    value=None
    while True:
        value=inputstream.read(1)
        value=struct.unpack('B',value)[0]
        result|=(value&0x7f)<<bitsRead
        bitsRead+=7
        if value&0x80==0:
            break
    return result

def readString(inputstream):
    length=read7BitEncodedInt(inputstream)
    if length<0:
        return None
    if length==0:
        return ''
    data=inputstream.read(length)
    return data.decode()

def readXNB(inputstream):
    # check XNB Flag
    XNBFlag=inputstream.read(3)
    if XNBFlag!=b'XNB':
        raise XNBFormatException('Not a XNB file')
    # check Target Platform
    targetPlatform=inputstream.read(1)
    if not targetPlatform in (b'w',b'm'):
        raise XNBFormatException('Target Platform not match.')
    # check XNB version
    XNBFormatVersion=inputstream.read(1)
    if XNBFormatVersion!=b'\x05':
        raise XNBFormatException('XNB version not right.')
    # check Flag Bits
    flagBits=inputstream.read(1)
    if flagBits!=b'\x00' and flagBits!=b'\x01':
        raise XNBFormatException('Flag Bits not right.')
    # ship file size
    compressedFileSize=readUInt32(inputstream)
    # check Type Reader count
    typereaderCount=read7BitEncodedInt(inputstream)
    if typereaderCount!=1:
        raise XNBFormatException('More than one Typereader.')
    # get Type Reader name
    readerName=readString(inputstream)
    if not readerName in ('Microsoft.Xna.Framework.Content.StringReader',
            'Game.XElementReader, Game'):
        raise XNBFormatException('Unknown Type Reader.')
    # ship Type Reader version
    readerVersionNumber=readInt32(inputstream)
    # check Shared Resource count
    sharedResourceCount=read7BitEncodedInt(inputstream)
    if sharedResourceCount!=0:
        raise XNBFormatException('Shared Resource count is not zero')
    typeReaderIndex=read7BitEncodedInt(inputstream)
    if typeReaderIndex!=1:
        raise XNBFormatException('Type Reader Index not match')
    data=readString(inputstream)
    return (targetPlatform,readerName,data)

def writeUInt32(outputstream,value):
    data=struct.pack('I',value)
    outputstream.write(data)

def writeInt32(outputstream,value):
    data=struct.pack('i',value)
    outputstream.write(data)

def write7BitEncodedInt(outputstream,value):
    num=value
    while num>=128:
        data=struct.pack('B',(num|128)&0xff)
        outputstream.write(data)
        num>>=7
    data=struct.pack('B',num&0xff)
    outputstream.write(data)

def writeString(outputstream,value):
    write7BitEncodedInt(outputstream,len(value))
    outputstream.write(value.encode())

def writeXNB(outputstream,targetPlatform,readerName,data):
    # XNB Flag
    outputstream.write(b'XNB')
    # Target platform
    outputstream.write(targetPlatform)
    # XNB format version
    outputstream.write(b'\x05')
    # Flag bits
    if targetPlatform==b'm':
        outputstream.write(b'\x00')
    else:
        outputstream.write(b'\x01')
    # file size, write it later
    writeUInt32(outputstream,0)
    # Type Reader count
    write7BitEncodedInt(outputstream,1)
    # Type Reader name
    writeString(outputstream,readerName)
    # Reader version number
    writeInt32(outputstream,0)
    # Shared resource count
    write7BitEncodedInt(outputstream,0)
    # Type Reader Index
    write7BitEncodedInt(outputstream,1)
    # the String data
    writeString(outputstream,data)
    # write file size
    size=outputstream.tell()
    outputstream.seek(6)
    writeUInt32(outputstream,size)

def expandStream(oldstream):
    oldstream.readUInt32=readUInt32
    oldstream.readInt32=readInt32
    oldstream.read7BitEncodedInt=read7BitEncodedInt
    oldstream.readString=readString
    oldstream.readXNB=readXNB

    oldstream.writeUInt32=writeUInt32
    oldstream.writeInt32=writeInt32
    oldstream.write7BitEncodedInt=write7BitEncodedInt
    oldstream.writeString=writeString
    oldstream.writeXNB=writeXNB
