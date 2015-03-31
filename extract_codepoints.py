#!/usr/bin/env python

from struct import pack, unpack
import json, sys

import math
from PIL import Image

def extract_codepoints(font):
    version = unpack('B', font.read(1))[0]
    max_height = unpack('B', font.read(1))[0]
    numbers = unpack('H', font.read(2))[0]
    wildcard = unpack('H', font.read(2))[0]

    table_size = unpack('B', font.read(1))[0]
    codepoint_bytes = unpack('B', font.read(1))[0]

    print >>sys.stderr, 'Contains %d codepoints' % numbers
    print >>sys.stderr, 'Maximum height: %d' % max_height

    codepoints = []

    hash_table = {}
    for i in range(table_size):
        index = unpack('B', font.read(1))[0]
        size = unpack('B', font.read(1))[0]
        offset = unpack('H', font.read(2))[0]
        hash_table[index] = (size, offset)

    table_offset = 0x08 + table_size*0x04
    offset_tables = {}
    for index in hash_table:
        size, offset = hash_table[index]
        font.seek(table_offset+offset)

        offset_table = []
        for j in range(size):
            if codepoint_bytes == 4:
                codepoint, offset = unpack('<II', font.read(8))
            else:
                codepoint, offset = unpack('<HI', font.read(6))
            offset_table.append((codepoint, offset))
            codepoints.append(codepoint)
        offset_tables[index] = offset_table

    for index in hash_table:
        size, offset = hash_table[index]
        table_offset += (codepoint_bytes+4)*size

    gap = int(max_height*1.5)
    side = int(math.sqrt(numbers))
    if side*side < numbers:
        side += 1
    bitmap = Image.new('RGB', (side*gap, side*gap), 'white')

    count = 0
    for index in hash_table:
        size, offset = hash_table[index]
        offset_table = offset_tables[index]
        for j in range(size):
            codepoint, offset = offset_table[j]
            font.seek(table_offset+offset)
            width, height, left, top = unpack('<BBbb', font.read(4))
            advance = unpack('b', font.read(1))[0]

            size = width*height
            size = (size+7)/8
            data = font.read(size)

            for y in range(height):
                for x in range(width):
                    off = x+y*width
                    bit = ord(data[off/8]) & (0x01 << (off%8))
                    if bit > 0:
                        bitmap.putpixel((count/side*gap+x+left, count%side*gap+y+top), (0,0,0))

            count += 1

    bitmap.show()

    print json.dumps({
            'max_height': max_height,
            'codepoints': codepoints,
            'characters': [unichr(cp) for cp in codepoints]
        }, indent=4, ensure_ascii=False).encode('utf-8')

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print 'Usage: extract_codepoints.py fontfile > codepoints.json'
        exit()

    file_name = sys.argv[1]
    font = open(file_name, 'rb')
    extract_codepoints(font)

