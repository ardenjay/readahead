#!/usr/bin/env python
#
# Copyright (C) 2018 Jay Tu
#

#import adb
import re
import sys
import bisect

class Io:
    def __init__(self):
        self.dev = 0
        self.ino = 0
        self.ofs = []

    def add_io(self, dev, ino, ofs):
        self.dev = dev
        self.ino = ino
        if not ofs in self.ofs:
            bisect.insort(self.ofs, int(ofs))

    def dump(self):
        print("dev ({0}), ino ({1}) - offset:".format(self.dev, self.ino))
        for i in self.ofs:
            print i,
        print "\n"

class PgParser:
    def __init__(self):
        self.pid = 0
        self.files = {}  # k: ino, v: [] of file ofs

    def process(self, pid, dev, ino, off):
        self.pid = pid
        if ino in self.files:
            f = self.files[ino]
            f.add_io(dev, ino, off)
        else:
            f = Io()
            f.add_io(dev, ino, off)
            self.files[ino] = f

class FilePg:
    parser = {}  # k: pid, v: [] of PgParser

    def parse(self, line):
        RE_PID = r'.+-([0-9]+)'
        SPACE = r'\s*'
        WILD_CHAR = '.*'
        KEY_WORD = r'mm_filemap_add_to_page_cache: dev '
        DEV = r'([0-9]+:[0-9]+)'
        INO = r'ino ([0-9a-z]+)'
        OFF = r'ofs=([0-9]+)'

        RE = RE_PID + SPACE + WILD_CHAR + KEY_WORD + DEV + SPACE + INO + WILD_CHAR + OFF
        re_obj = re.compile(RE)
        match_obj = re_obj.match(line)
        if match_obj is None:
            return False

        try:
            pid = match_obj.group(1)
            dev = match_obj.group(2)
            ino = match_obj.group(3)
            off = match_obj.group(4)
        except Exception, e:
            print "Error while re parse: " + str(e)
            return False
        else:
            if pid in self.parser:
                p = self.parser[pid]
                p.process(pid, dev, ino, off)
            else:
                p = PgParser()
                p.process(pid, dev, ino, off)
                self.parser[pid] = p

    def dump(self):
        for p in self.parser:
            parser_obj = self.parser[p]
            print ("dump for {0}:".format(parser_obj.pid))
            for f in parser_obj.files:
                parser_obj.files[f].dump();

def main(argv):
    if (len(argv) < 2):
	print "inof.py filename"
        return

    filename = argv[1]

    '''
    device = adb.get_device()
    if device is None:
        sys.exit("ERROR: Failed to find device.")

    output, _ = device.shell(['/data/inof.sh'])
    '''
    parser = FilePg()

    with open(filename) as f:
        for l in f:
            parser.parse(l)
    parser.dump()

if __name__ == "__main__":
    main(sys.argv)
