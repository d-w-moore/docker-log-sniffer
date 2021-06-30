from __future__ import print_function
import posix
from os import SEEK_SET, SEEK_END
import getopt
import tarfile
import docker
import sys
import tempfile
import io

# extract options
#   -v for verbose and -o '' for no output, 
# arguments (1 <= #arg <=2): image_name [ desired_path_of_file_to_be_output ]

opts,args = getopt.getopt(sys.argv[1:],'vo:',['permanent_output_tarfile=','tar_snoop_and_exit'])

o_opt = dict(opts).get('-o','')                          # -o default: no output (/dev/null)
v_opt = (dict(opts).get('-v') is not None)               # -v default: not verbose
p_opt = dict(opts).get('--permanent_output_tarfile','')  # default is not to keep the temp tarfile

opt_TAR_snoop_and_exit = (dict(opts).get('--tar_snoop_and_exit',None) is not None)

output = open(o_opt,'wb') if o_opt not in ('-','') \
                          else (sys.stdout if o_opt == '-' else open('/dev/null','wb'))

#--------------- Get handle to coontainer's internal dir/file hierarchy

docker_client = docker.client.from_env()

if list(args) == []: print ('must specify container name',sys.stderr);
some_container = docker_client.containers.get(args[0])

#--------------- write tarfile content to buffer (with option for permanence)

arch = some_container.get_archive('/')
container_tree_iter = arch[0]
if p_opt:
    temp_store = open(p_opt,'w+b')
else:
    temp_store = tempfile.SpooledTemporaryFile()
for x in container_tree_iter:
    temp_store.write(x)
temp_store.flush()

temp_store.seek(0,SEEK_SET)

tar_file = tarfile.open( fileobj = temp_store )

tar_iter = iter(tar_file)

#--------------- [--tar-snoop] option detects #files and tar size, then exits

if opt_TAR_snoop_and_exit:
    print ('tarfile entries total = ',len([entry for entry in tar_iter]))
    temp_store.seek(0,SEEK_END)
    print ('tarfile bytes total   = ',temp_store.tell())
    exit()

member_for_output = None

# Iterate through TAR content to find the path specified.
# ( Quitting iteration when it's found, so not using the "for thing in iterable" syntax : )
try:
    while True: 
        tar_info = next(tar_iter)
        if v_opt: print(tar_info.path, file = sys.stderr)
        if args[1:] and tar_info.path == args[1]:
            if v_opt: print('Info: specified path',args[1], 'found !!', file = sys.stderr)
            member_for_output = tar_info
            break
except StopIteration:
    pass

# ---- COPY contents of container file @ desired path to the host filesystem

if member_for_output is not None:
        s = tar_file.extractfile( member_for_output ).read()
        import hashlib
        m = hashlib.md5()
        m.update(s)
        if posix.isatty(output.fileno()):
            print('reading file of size' , len(s),file=sys.stderr)
            print('  and md5 digest =  ' , m.hexdigest(),file=sys.stderr)
        else:
            output.write(s)
else:
    if args[1:]: print('Warning: specified path',args[1], 'was not found', file = sys.stderr)

