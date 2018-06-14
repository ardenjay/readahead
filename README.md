# readahead

The purpose is to make device boot faster.

One of the boot process is to load data from external storage to memory. This checks which portion of file is loaded into page cache and tries to read it in advance.

Overall process:

                             trace_event=mm_filemap_add_to_page_cache
                                            +
                                            |
                                            |
                                            |
                                 +----------v----------+
                                 |                     |
                                 |        Ftrace       |
                                 |                     |
                                 +----------+----------+
                                            |
                                            |
                                            | trace file
                                            |
                                            v
                                 +----------+----------+
                                 |                     |
                                 |       inof.py       |
                                 |                     |
                                 +----------+----------+
                                            |
                                            |
                                            | readahead file list
                                            |
                                            |
                                +-----------v--------------+
                                |                          |
                                |   readahead system call  |
                                |                          |
                                +-----------+--------------+
                                            |
                                            |
                                            |
                                            v




Sample output for inof.py for parsing test/page_cache_output for PID 236:

dump for 236:
/system, file: ./lib/libc.so - offset:
131072 135168 139264 143360 147456 151552 155648 159744 163840 167936 172032 176128 180224 184320 188416 192512 196608 200704 204800 208896 212992 217088 221184 225280 229376 233472 237568 241664 245760 249856 253952 258048 262144 266240 270336 274432 278528 282624 286720 290816 294912 299008 303104 307200 311296 315392 319488 323584 327680 331776 335872 339968 344064 348160 352256 356352 360448 364544 368640 372736 376832 380928 385024 389120 393216 397312 401408 405504 409600 413696 417792 421888 425984 430080 434176 438272 442368 446464 450560 454656 458752 462848 466944 471040 475136 479232 
