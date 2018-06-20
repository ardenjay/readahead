#!/usr/bin/env python
#
# Copyright (C) 2018 Jay Tu
#

import adb
import re
import sys
import bisect
import argparse

SYSTEM_DEV = r'179:35'
DEVICE_MAPPING = {SYSTEM_DEV: r'/system'}


class Io:
    def __init__(self, dev):
        self.dev = 0
        self.ino = 0
        self.ofs = []
        self.part = ""
        self.device = dev
        self.file_name = ""

    def get_file_name(self):
        if not self.part:
            return

        path = self.part
        ino_hex = int(self.ino, 16)      # ino is the hex string
        s_ino_hex = hex(ino_hex)
        output, _ = self.device.shell(['/data/get_file.sh', path, s_ino_hex])
        if output:
            self.file_name = output.rstrip()

    def add_io(self, dev, ino, off):
        self.dev = dev
        if self.dev in DEVICE_MAPPING:
            self.part = DEVICE_MAPPING[self.dev]

        if self.part:
            self.ino = ino
            self.get_file_name()

        ofs = int(off)
        if ofs not in self.ofs:
            bisect.insort(self.ofs, ofs)

    def dump(self):
        if not self.part:
            print("dev ({0}), ino ({1}) - offset:".format(self.dev, self.ino))
        else:
            print("{0}, file: {1} - offset:".format(self.part, self.file_name))
        for i in self.ofs:
            print i,
        print "\n"


class PgParser:
    def __init__(self):
        self.pid = 0
        self.dev = 0
        self.ino = 0
        self.file_name = ""
        self.off = 0
        self.files = {}  # k: ino, v: [] of file ofs
        self.device = adb.get_device()

    def process(self, pid, dev, ino, off):
        if ino in self.files:
            f = self.files[ino]
            f.add_io(dev, ino, off)
        else:
            f = Io(self.device)
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

        RE = RE_PID + SPACE + WILD_CHAR + KEY_WORD + DEV + \
            SPACE + INO + WILD_CHAR + OFF
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
        if res:
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

    def out(self, outfile):
        print outfile


def process_cmdline():
    argp = argparse.ArgumentParser(description="page cache parser")
    argp.add_argument('--file', dest='filename',
            help='the page cache file that ftrace output')
    argp.add_argument('--output', dest='outfile',
            help='output the parser result to file')
    return argp.parse_args()


def main(argv):
    argp = process_cmdline()

    filename = argp.filename

    parser = FilePg()

    with open(filename) as f:
        lineno = 0
        for l in f:
            parser.parse(l)
            print 'Parsed {0} lines\r'.format(lineno),
            sys.stdout.flush()
            lineno += 1
    print 'Done............................................'

    parser.dump()

    if argp.outfile:
        parser.out(argp.outfile)


if __name__ == "__main__":
    main(sys.argv)
