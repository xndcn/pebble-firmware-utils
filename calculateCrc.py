#!/usr/bin/env python

import sys
from libpebble.stm32_crc import crc32

if len(sys.argv) <= 1 or sys.argv[1] == '-h':
	print 'calculateCrc.py calculates STM32 CRC sum for a given file or stdin'
	print 'Usage: calculateCrc.py filename'
	print 'Use `-\' as filename to read from stdin.'
	exit()

filename = sys.argv[1]
f = sys.stdin if filename == '-' else open(filename, 'rb')
c = crc32(f.read())
print 'Checksum for %s:' % (filename if filename!='-' else '<stdin>')
print 'Hex: 0x%08X\nDec: %d' % (c, c)
