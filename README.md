# docker-log-sniffer

Allows:

   - iterating through filesystem of a container
   - selecting a path of the tree to be output via [-o output_name]
   - optionally streaming the entire container's filesystem out into a [--permanent tar_file_by_name]

```
$ docker run --name my_container ubuntu:18.04
    # dd if=/dev/urandom of=/abc.dat  bs=1k count=500
    # od -vtx1 < /abc.dat > /tmp/abc.dat
    # exit

$ python get_archive.py -v my_container
  [ ... spools out all paths in the container's filesystem to STDERR ]
  
$ python get_archive.py -o host_vsn_abc.dat  --perm=out.tar  my_container  /tmp/abc.dat

$ python get_archive.py -o host_vsn_abc.dat2  my_container  /tmp/abc.dat  ###  SAME BUT OMITTING --perm keeps things in a tempfile

$ docker cp my_container:/tmp/abc.dat check_me  
$ diff3 host_vsn_abc.dat* check_me

```
