#!/usr/bin/env python

import sys
import os, os.path
import json
from subprocess import call

def fail(msg = "Failed."):
	print msg
	exit(1)

def analyzeResources(useManifest, pathToRes):
	r = []
	if useManifest:
		with open("manifest.json", "r") as f:
			manifest = json.load(f)
		if "resourceMap" in manifest["debug"]:
			rm = manifest["debug"]["resourceMap"]["media"]
		else:
			print "##########################################################"
			print "      Error!!! Manifest contains no resourceMap!"
			print "It must be a 2.0 firmware! Don't use this method with it!"
			print "##########################################################"
			rm = []
			fail() # if you want to make this a warning rather an error, remove this line
		for i in rm:
			item = {"type": "raw",
				"defName": i["defName"],
				"file": os.path.dirname(i["file"]) + "/" + i["defName"]}
			if os.path.exists(item["file"]):
				print "Adding resource %s as %s..." % (i['file'], i['defName'])
				r.append(item)
				fullpath = pathToRes + "/" + item["file"]
				if not os.path.exists(os.path.dirname(fullpath)):
					os.mkdir(os.path.dirname(fullpath))
				os.link(item["file"], fullpath)
	if os.path.isdir("res"):
		files = os.listdir("res")
		filter(lambda x: len(x)>4 and x[0].isdigit() and x[1].isdigit() and x[2]=="_", files)
		files.sort()
		for i in files:
			n = int(i[:2])
			if n < len(r):
				continue
			item = {"type": "raw",
				"defName": i,
				"file": "res/" + i}
			print "Adding resourse %s..." % i
			r.append(item)
			fullpath = pathToRes + "/" + item["file"]
			if not os.path.exists(os.path.dirname(fullpath)):
				os.mkdir(os.path.dirname(fullpath))
			os.link(item["file"], fullpath)
	return r

def ver1(sdk):
	cpr = sdk+"../tools/create_pebble_project.py"
	if not os.path.isfile(cpr):
		print "This doesn't look like a usable Pebble 1.x SDK:"
		print "Couldn't read " + cpr
		exit(1)
	
	if os.path.exists("app"):
		fail("./app/: path already exists!")

	print " # Creating project..."
	call([cpr, sdk, "app"]) == 0 or fail()

	print " # Analyzing resources..."
	res = analyzeResources(True, "app/resources/src")
	print res

	print " # Populating resource data..."
	with open("app/resources/src/resource_map.json", "r+") as f:
		obj = json.load(f)
		obj['media'] = res
		obj['friendlyVersion'] = "v1.10-JW"
		#obj['versionDefName'] = "v1.10-JW" # buggy
		f.seek(0)
		json.dump(obj, f, indent=4)

	print " # Configuring project..."
	os.chdir("app")
	call("./waf configure", shell=True) == 0 or fail()
	print " # Building project..."
	call("./waf build", shell=True) == 0 or fail()

def ver2(sdk):
	print "Not implemented yet."
	pass

if __name__ == "__main__":
	if len(sys.argv) < 3 or sys.argv[1] == "-h":
		print "Usage: %s ( -1 | -2 ) /path/to/Pebble/SDK/" % __file__
		print "Assuming that current directory is one with unpacked firmware."
		print "Will create a new project in directory `app' and configure it to pack resources."
		exit()
	sdk = sys.argv[2]
	if not os.path.isdir(sdk):
		print "%s is not a directory!" % sdk
		exit(1)
	if sys.argv[1] == "-1":
		ver1(sdk)
	elif sys.argv[1] == "-2":
		ver2(sdk)
	else:
		print "Illegal argument, try -h"
		exit(1)
	
	print " # Creating symlink..."
	if os.path.exists("../system_resources.new.pbpack"):
		print "Already exists."
	else:
		os.symlink("app/build/app_resources.pbpack", "../system_resources.new.pbpack")
	print " # Done! You may get pbpack at system_resources.new.pbpack"
	print "   Also you may rebuild it with:  cd app; ./waf build"
