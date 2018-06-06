#!/usr/bin/env python
#
# Copyright (C) 2018 Jay Tu
#

import adb

def main():

    device = adb.get_device()
    if device is None:
        sys.exit("ERROR: Failed to find device.")

    output, _ = device.shell(['/data/inof.sh'])

if __name__ == "__main__":
    main()
