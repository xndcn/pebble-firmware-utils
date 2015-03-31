#!/usr/bin/env python

import argparse, os
import sys

if 'PEBBLE_SDK_PATH' not in os.environ:
    print 'Please set pebble sdk path environment variable firstly!'
    print 'export PEBBLE_SDK_PATH=/path/to/PebbleSDK/'
    sys.exit()

sys.path.append(os.path.join(os.environ['PEBBLE_SDK_PATH'], 
                'Pebble/common/tools'))
from pbpack import ResourcePack

def makedirs(directory):
    try:
        os.makedirs(directory)
    except:
        pass

def cmd_unpack(args):
    with open(args.pack_file, 'rb') as pack_file:
        pack = ResourcePack.deserialize(pack_file)
        makedirs(args.output_directory)
        for i in range(len(pack.contents)):
            with open(os.path.join(args.output_directory, '%03d' % i), 'wb') as content_file:
                content_file.write(pack.contents[i])

def cmd_pack(args):
    pack = ResourcePack()
    for f in args.pack_file_list:
        pack.add_resource(open(f, 'rb').read())
    with open(args.pack_file, 'wb') as pack_file:
        pack.serialize(pack_file)

def main():
    parser = argparse.ArgumentParser(description="Pack and Unpack"
                                                 "pbpack file")
    subparsers = parser.add_subparsers(help="commands", dest='which')

    unpack_parser = subparsers.add_parser('unpack',
                                          help="unpack the pbpack file")
    unpack_parser.add_argument('pack_file', metavar="PACK_FILE",
                               help="File to unpack")
    unpack_parser.add_argument('output_directory', metavar="OUTPUT_DIRECTORY",
                               help="Directory to write the contents to")
    unpack_parser.set_defaults(func=cmd_unpack)

    pack_parser = subparsers.add_parser('pack',
                                         help="pack the pbpack file")
    pack_parser.add_argument('pack_file', metavar='PACK_FILE',
                              help="file to write the pbpack to")
    pack_parser.add_argument('pack_file_list', metavar='PACK_FILE_LIST',
                              nargs="*", help="a list of <pack_file_path>s")
    pack_parser.set_defaults(func=cmd_pack)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
