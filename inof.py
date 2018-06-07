#!/usr/bin/env python
#
# Copyright (C) 2018 Jay Tu
#

#import adb
import re

data = r'     logd-236   [000] ....    15.154805: mm_filemap_add_to_page_cache: dev 179:35 ino 6db page=f76e7ac0 pfn=321622 ofs=348160'

class Io:
    dev = 0
    ino = 0
    ofs = []

    def __init__(self, dev, ino, off):
        self.dev = dev
        self.ino = ino
        self.ofs.append(off)

    def dump(self):
        print("dev ({0}), ino ({1}) - ".format(self.dev, self.ino))
        for i in self.ofs:
            print "offset: " + i

class PgParser:
    def __init__(self):
        self.pid = 0
        self.parser = {}  # k: pid, v: [] of PgParser
        self.files  = {}  # k: ino, v: [] of file ofs

    def process(self, pid, dev, ino, off):
        print ("ADD PID: {0} dev({1}) {2}:{3}".format(pid, dev, ino, off))
        self.pid = pid
        f = Io(dev, ino, off)
        if not f.ino in self.files:
            self.files[ino] = f

    def insert(self):
        if not self.pid in self.parser:
            self.parser[self.pid] = self

    def dump(self):
        for p in self.parser:
            parser_obj = self.parser[p]
            print ("dump for {0}:".format(parser_obj.pid))
            for f in parser_obj.files:
                parser_obj.files[f].dump();

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
            name = match_obj.group(1)
            dev  = match_obj.group(2)
            ino  = match_obj.group(3)
            off  = match_obj.group(4)
        except Exception, e:
            print "Error while re parse: " + str(e)
            return False
        else:
            self.process(name, dev, ino, off)
            self.insert()

def main():
    '''
    device = adb.get_device()
    if device is None:
        sys.exit("ERROR: Failed to find device.")

    output, _ = device.shell(['/data/inof.sh'])
    '''

    parser = PgParser()
    parser.parse(data)
    parser.dump()

if __name__ == "__main__":
    main()
