#!/usr/bin/env python

import zipfile, zlib
import os, os.path, sys, io
import json
from libpebble.stm32_crc import crc32
from struct import pack, unpack
import tempfile
import shutil

def getCrc(pbpack):
	"""read CRC from a pbpack file"""
	pbpack.seek(4)
	return unpack('I', pbpack.read(4))[0]

def updateCrc(tintin, nOld, nNew):
	"""update CRC sum in tintin binary"""
	old = pack('I', nOld)
	new = pack('I', nNew)
	fw = tintin.read()
	i = fw.find(old)
	if i < 0:
		print "Oops... Couldn't find checksum 0x%08X in tintin_fw.bin! Maybe you specified incorrect data?.."
		exit(1)
	j = fw.find(old, i+1)
	if not j < 0: # if it was not the only occurance
		print "Oops... There are several occurances of possible checksum 0x%08X, at least at 0x%08X and 0x%08X." % (nOld, i, j)
		print "Bailing out!"
		exit(1)
	print "Found the only occurance of old checksum 0x%08X at 0x%08X" % (nOld, i)
	print "Replacing it with the new value 0x%08X..." % nNew
	tintin.seek(i)
	tintin.write(new)
	tintin.flush()
	print "OK."

def parse_args():
	def readable(f):
		open(f, 'rb').close()
		return f
	import argparse
	parser = argparse.ArgumentParser(description="Update checksums and pack firmware package with modified resource pbpack file")
	parser.add_argument("outfile",
			help="Output file, e.g. Pebble-1.10-ev2_4.pbz")
	parser.add_argument("respack", type=readable,
			help="Updated resource pack filename, e.g. app_resources.pbpack")
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-o", "--original", type=argparse.FileType('rb'),
			help="Original resource pack from the original firmware", metavar="ORIGINAL_RESPACK")
	group.add_argument("-c", "--orig-crc", type=lambda x: int(x,16),
			help="CRC sum from the original resource pack (hexadecimal), e.g. 0xDEADBE05", metavar="0xDEF01234")
	parser.add_argument("-m", "--manifest", default="manifest.json", type=readable,
			help="Manifest file from the original firmware, defaults to manifest.json")
	parser.add_argument("-t", "--tintin-fw", "--tintin", default="tintin_fw.bin", type=readable,
			help="Tintin_fw file from the original firmware, defaults to tintin_fw.bin")
	group = parser.add_argument_group("Optional parameters")
	group.add_argument("-k", "--keep-dir", action="store_true",
			help="Don't remove temporary directory after work")
	return parser.parse_args()

if __name__ == "__main__":
	args = parse_args()
	if args.original:
		args.orig_crc = getCrc(args.original)
		args.original.close()
	
	print "Will create firmware at %s," % args.outfile
	print "using %s for manifest, %s for tintin binary" % (args.manifest, args.tintin_fw)
	print "and %s for resource pack" % args.respack 
	print

	try:
		workdir = tempfile.mkdtemp()+'/'

		print " # Copying new resource pack..."
		shutil.copy(args.respack, workdir+'system_resources.pbpack')
		with open(workdir+'system_resources.pbpack', 'rb') as newres:
			newCrc = getCrc(newres)

		print " # Copying tintin_fw.bin..."
		shutil.copy(args.tintin_fw, workdir+'tintin_fw.bin')
		print " # Updating CRC value in tintin_fw.bin from 0x%08X to 0x%08X:" % (args.orig_crc, newCrc)
		with open(workdir+'tintin_fw.bin', 'r+b') as tintin:
			updateCrc(tintin, args.orig_crc, newCrc)

		print " # Reading manifest..."
		with open(args.manifest, 'r') as f:
			manifest = json.load(f)

		print " # Updating manifest..."
		rp_size = os.path.getsize(args.respack)
		print "   res pack size = %d" % rp_size
		with open(args.respack) as f:
			rp_crc = crc32(f.read())
		print "   res pack crc = %d" % rp_crc
		with open(workdir+"tintin_fw.bin") as f:
			tintin_crc = crc32(f.read())
		print "   tintin crc = %d" % tintin_crc

		print " # Changing values:"
		print "  resources.size: %d => %d" % (manifest['resources']['size'], rp_size)
		manifest['resources']['size'] = rp_size
		print "  resources.crc: %d => %d" % (manifest['resources']['crc'], rp_crc)
		manifest['resources']['crc'] = rp_crc
		print "  firmware.crc: %d => %d" % (manifest['firmware']['crc'], tintin_crc)
		manifest['firmware']['crc'] = tintin_crc

		print " # Storing manifest..."
		with open(workdir+"manifest.json", "wb") as f:
			json.dump(manifest, f)
		
		print " # Creating output zip..."
		with zipfile.ZipFile(args.outfile, "w", zipfile.ZIP_STORED) as z:
			for f in ("tintin_fw.bin", "system_resources.pbpack", "manifest.json"):
				print "   Storing %s..." % f
				z.write(workdir+f, f)

		print " # Done. Firmware is packed to %s" % args.outfile

	finally:
		if args.keep_dir:
			print "Kept temporary files in %s" % workdir
		else:
			print "Removing temporary files..."
			shutil.rmtree(workdir)

