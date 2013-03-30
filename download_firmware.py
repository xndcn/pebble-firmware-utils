#!/usr/bin/env python
# URI = 'http://pebble-static.s3.amazonaws.com/watchfaces/index.html'
URI = 'http://pebblefw.s3.amazonaws.com/pebble/ev2_4/release/latest.json'

from urllib2 import urlopen
import hashlib
import logging, os.path
import json

if __name__ == "__main__":
    log = logging.getLogger()
    logging.basicConfig(format='[%(levelname)-8s] %(message)s')
    log.setLevel(logging.DEBUG)
    
    log.info("Downloading firmware linked from %s" % URI)
    
    page = urlopen(URI).read()
    data = json.loads(page)
    
    firmware = data['normal']['url']
    version  = data['normal']['friendlyVersion']
    sha      = data['normal']['sha-256']
    
    log.info("Latest firmware version: %s" % version)
    fwfile = firmware[firmware.rindex("/")+1:]
    if os.path.exists(fwfile):
        log.warn('Did not download "%s" because it would overwrite an existing file' % fwfile)
        exit()
    with open(fwfile, "wb") as f:
        log.info("Downloading %s -> %s" % (firmware, fwfile))
        f.write(urlopen(firmware).read())
    
    f = open(fwfile, "rb")
    filesha = hashlib.sha256()
    filesha.update(f.read())
    if(filesha.hexdigest() != sha):
        log.error('File download errer: SHA-256 hash mismatch. Please retry.')
    