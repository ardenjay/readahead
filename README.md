# readahead

The purpose is to make device boot faster.

One of the boot process is to load data from external storage to memory. This checks which portion of file is loaded into page cache
and tries to read it in advance.
