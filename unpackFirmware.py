#!/usr/bin/env python

import zipfile, zlib
import os, sys, io
import json
from libpebble.stm32_crc import crc32
from struct import pack, unpack


def mkdir(path):
	try:
		os.mkdir(path)
	except OSError:
		pass
		
def extract_content(pbz, content, output_dir):
	print 'Extracting %s...' % content['name']
	pbz.extract(content['name'], output_dir)
	data = io.FileIO(output_dir + content['name']).readall()
	crc = crc32(data)
	if crc == content['crc']:
		print '\t[  OK] Checking CRC...'
	else:
		print '\t[Fail] Checking CRC...'
		print "\tIt's %d, but should be %d" % (content['crc'], crc)

def extract_resources(pbpack, resourceMap, output_dir):
	numbers = unpack('B', pbpack.read(1))[0]
	print 'Resource pack has %d resources.' % numbers

	pbpack.seek(4)
	crc_from_json = unpack('I', pbpack.read(4))[0]
	print 'Resource pack claims to have crc 0x%X.' % crc_from_json

	offset=None # this will be set depending on firmware version

	print 'Checking CRC with offset 0x100C (2.x)...'
	pbpack.seek(0x100C)
	crc_resource = crc32(pbpack.read())
	if crc_resource == crc_from_json:
		print '\t[  OK] This seems to be a 2.x firmware.'
		offset = 0x0C
	else:
		print '\t[Info] It is not 2.x firmware, or is corrupted, CRC=0x%08X' % crc_resource
		print 'Checking CRC with offset 0x101C (1.x)...'
		pbpack.seek(0x101C)
		crc_resource2 = crc32(pbpack.read())
		if crc_resource2 == crc_from_json:
			print '\t[  OK] This seems to be a 1.x firmware.'
			offset = 0x1C
		else:
			print '\t[Fail] CRC check failed!'
			print "\tShould be 0x%X, but if 0x%X for 100c and 0x%x for 101c." % (
					crc_from_json, crc_resource, crc_resource2)
			print 'Resource pack is either malformed or has unknown format.'
			return

	print 'Reading resurce headers...'
	resources = {}
	for i in range(numbers):
		pbpack.seek(offset + i * 16)
		index = unpack('i', pbpack.read(4))[0] - 1
		resources[index] = {
			'offset': unpack('i', pbpack.read(4))[0],
			'size': unpack('i', pbpack.read(4))[0],
			'crc': unpack('I', pbpack.read(4))[0]
		}

	for i in range(len(resources)):
		entry = resources[i]
		hasRM = resourceMap and i < len(resourceMap)
		path = resourceMap[i]['file'] if hasRM else 'res/%02d_%08X' % (i, entry['crc'])
		dirname = os.path.dirname(path)
		filepath = "/".join((dirname, resourceMap[i]['defName'])) if hasRM else path

		print 'Extracting %s...' % filepath
		mkdir(output_dir + dirname)

		pbpack.seek(0x1000 + offset + entry['offset'])
		file = open(output_dir + filepath, 'wb')
		file.write(pbpack.read(entry['size']))
		file.close()

		data = io.FileIO(output_dir + filepath).readall()
		crc = crc32(data)
		if crc == entry['crc']:
			print '\t[  OK] Checking CRC...'
		else:
			print '\t[Fail] Checking CRC...'
			print "\tIt's 0x%x, but should be 0x%x" % (crc, entry['crc'])
	print 'All resources unpacked.'
		

if __name__ == '__main__':
	useNaming = True
	if len(sys.argv) > 1 and sys.argv[1] == '-i':
		useNaming = False
		sys.argv.pop(1)

	if len(sys.argv) <= 1:
		print 'Usage: unpackFirmware.py [-i] normal.pbz [output_dir/]'
		print '    -i: ignore resource filenames from manifest.'
		print '       By default, if manifest contains resource names'
		print '       (as in 1.x firmwares), we will name resources'
		print '       according to them.'
		print '       With this option, resource names will be res/ID_CRC'
		print '       where ID is sequence index of resource and CRC is'
		print '       its CRC checksum (for comparing)'
		print '       On 2.x firmwares, which don\'t contain resource names,'
		print '       we always use that scheme.'
		exit()

	pbz_name = sys.argv[1]
	if len(sys.argv) <= 2:
		output_dir = 'pebble-firmware/'
	else:
		output_dir = sys.argv[2]
		if not output_dir.endswith('/'):
			output_dir += '/'
	print 'Will unpack firmware from %s to directory %s, using %s for filenames' % (
			pbz_name, output_dir,
			'resource names (if possible)' if useNaming else 'resource indices')

	pbz = zipfile.ZipFile(pbz_name)

	print 'Extracting manifest.json...'
	pbz.extract('manifest.json', output_dir)
	manifest = json.load(open(output_dir + 'manifest.json', 'rb'))

	firmware = manifest['firmware']
	extract_content(pbz, firmware, output_dir)
	
	if 'resources' in manifest:
		resources = manifest['resources']
		extract_content(pbz, resources, output_dir)	
		
		if 'resourceMap' in manifest['debug']:
			resourceMap = manifest['debug']['resourceMap']['media']	
			print 'Found resource map in manifest. Looks like 1.x firmware.'
			if useNaming:
				print 'Will use it to name resources correctly. To ignore, pass -i option.'
			else:
				print 'Will not use it however because of -i option'
		else:
			resourceMap = None
			print "Couldn't find resource map in manifest. Looks like 2.x firmware."
			print 'Resources will be named by their indices.'
			useNaming = False
		pbpack = open(output_dir + resources['name'], 'rb')
		extract_resources(pbpack, resourceMap if useNaming else None, output_dir)
