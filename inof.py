#!/usr/bin/env python
#
# Copyright (C) 2018 Jay Tu
#

#import adb
import re
import sys
import bisect

SYSTEM_DEV = r'179:35'
DEVICE_MAPPING = {SYSTEM_DEV : r'/system'}

class Io:
    def __init__(self):
        self.dev = 0
        self.ino = 0
        self.ofs = []
        self.part = ""

    def add_io(self, dev, ino, off):
        self.dev = dev
        if self.dev in DEVICE_MAPPING:
            self.part = DEVICE_MAPPING[self.dev]
        self.ino = ino
        ofs = int(off)
        if not ofs in self.ofs:
            bisect.insort(self.ofs, ofs)

    def dump(self):
        if self.part == "":
            print("dev ({0}), ino ({1}) - offset:".format(self.dev, self.ino))
        else:
            print("{0}, ino ({1}) - offset:".format(self.part, self.ino))
        for i in self.ofs:
            print i,
        print "\n"

class PgParser:
    def __init__(self):
        self.pid = 0
        self.dev = 0
        self.ino = 0
        self.off = 0
        self.files = {}  # k: ino, v: [] of file ofs

    def process(self, pid, dev, ino, off):
        if ino in self.files:
            f = self.files[ino]
            f.add_io(dev, ino, off)
        else:
            f = Io()
            f.add_io(dev, ino, off)
            self.files[ino] = f

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
            self.pid = match_obj.group(1)
            self.dev = match_obj.group(2)
            self.ino = match_obj.group(3)
            self.off = match_obj.group(4)
        except Exception, e:
            print "Error while re parse: " + str(e)
            return False

        return True

    def dump(self):
        print ("dump for {0}:".format(self.pid))
        for f in self.files:
            io = self.files[f]
            io.dump()

class FilePg:
    parser = {}  # k: pid, v: [] of PgParser

    def parse(self, line):
        p = PgParser()
        res = p.parse(line)                     # begin parse the line
        if (res == True):
            pid = p.pid
            dev = p.dev
            ino = p.ino
            off = p.off
            if pid in self.parser:              # get the stored parser
                pgp = self.parser[pid]
                pgp.process(pid, dev, ino, off)
            else:
                p.process(pid, dev, ino, off)   # new parser
                self.parser[pid] = p            # stored the parser

    def dump(self):
        for p in self.parser:
            self.parser[p].dump()

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
