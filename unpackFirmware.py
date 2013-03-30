#!/usr/bin/python

import zipfile, zlib
import os, sys, io
import struct, json
from libpebble.stm32_crc import crc32


def mkdir(path):
	try:
		os.mkdir(path)
	except OSError:
		pass
		
def extract_content(pbz, content, output_dir):
	print 'Extracting %s...' % content['name']
	pbz.extract(content['name'], output_dir)
	data = io.FileIO(output_dir + content['name']).readall()
	if crc32(data) == content['crc']:
		print '\t[  OK] Checking CRC...'
	else:
		print '\t[Fail] Checking CRC...'

def extract_resources(pbpack, resourceMap, output_dir):
	numbers = struct.unpack('B', pbpack.read(1))[0]
	print 'Find %d resources.' % numbers

	resources = {}
	for i in range(numbers):
		pbpack.seek(0x1C + i * 16)
		index = struct.unpack('i', pbpack.read(4))[0] - 1
		resources[index] = {
			'offset': struct.unpack('i', pbpack.read(4))[0],
			'size': struct.unpack('i', pbpack.read(4))[0],
			'crc': struct.unpack('I', pbpack.read(4))[0]
		}

	for i in range(len(resourceMap)):
		path = resourceMap[i]['file']
		dirname = os.path.dirname(path)

		print 'Extracting %s...' % path
		mkdir(output_dir + dirname)

		entry = resources[i]
		pbpack.seek(0x101C + entry['offset'])
		file = open(output_dir + path, 'wb')
		file.write(pbpack.read(entry['size']))
		file.close()

		data = io.FileIO(output_dir + path).readall()
		if crc32(data) == entry['crc']:
			print '\t[  OK] Checking CRC...'
		else:
			print '\t[Fail] Checking CRC...'
		

if __name__ == '__main__':

	if len(sys.argv) <= 1:
		print 'usage: unpackFirmware.py normal.pbz [output_dir]'
		exit()

	pbz_name = sys.argv[1]
	if len(sys.argv) <= 2:
		output_dir = 'pebble-firmware/'
	else:
		output_dir = sys.argv[2] + '/'
	pbz = zipfile.ZipFile(pbz_name)

	print 'Extracting manifest.json...'
	pbz.extract('manifest.json', output_dir)
	manifest = json.load(open(output_dir + 'manifest.json', 'rb'))


	firmware = manifest['firmware']
	extract_content(pbz, firmware, output_dir)
	
	if 'resources' in manifest:
		resources = manifest['resources']
		extract_content(pbz, resources, output_dir)	
		
		resourceMap = manifest['debug']['resourceMap']['media']	
		pbpack = open(output_dir + resources['name'], 'rb')
		extract_resources(pbpack, resourceMap, output_dir)
