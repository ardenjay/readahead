#!/usr/bin/env python
#
# Copyright (C) 2018 Jay Tu
#

import adb
import re

data = r'     logd-236   [000] ....    15.154805: mm_filemap_add_to_page_cache: dev 179:35 ino 6db page=f76e7ac0 pfn=321622 ofs=348160'
def parse():
    RE_PID = r'.+-([0-9]+)'
    SPACE = r'\s*'

    RE = RE_PID + SPACE
    re_obj = re.compile(RE)
    match_obj = re_obj.match(data)

    print "match_obj : ", match_obj.group(1)

def main():
    device = adb.get_device()
    if device is None:
        sys.exit("ERROR: Failed to find device.")

    output, _ = device.shell(['/data/inof.sh'])

    parse()

if __name__ == "__main__":
    main()
