##############################################################################
# Copyright by The HDF Group.                                                #
# All rights reserved.                                                       #
#                                                                            #
# This file is part of H5Serv (HDF5 REST Server) Service, Libraries and      #
# Utilities.  The full HDF5 REST Server copyright notice, including          #
# terms governing use, modification, and redistribution, is contained in     #
# the file COPYING, which can be found at the root of the source code        #
# distribution tree.  If you do not have access to this file, you may        #
# request a copy from help@hdfgroup.org.                                     #
##############################################################################
import sys
import os
import stat
from shutil import copyfile
import h5py
import numpy as np

SRC = "../../testfiles"
DES = "../../data/test"

# files to be copied into test directory
testfiles = {
    'tall.h5': ('.',  'tall_updated.h5', 'tall_ro.h5', 'tall_g2_deleted.h5', 
            'tall_dset112_deleted.h5', 'tall_dset22_deleted.h5'),
    'tall_with_udlink.h5': ('.',),
    'scalar.h5': ('.', 'scalar_1d_deleted.h5',),
    'namedtype.h5': ('.', 'namedtype_deleted.h5'),
    'resizable.h5': ('.', 'resized.h5'),
    'notahdf5file.h5': ('.',),
    'zerodim.h5': ('filename with space.h5', 'deleteme.h5', 'readonly.h5', 'subdir',
    'subdir/deleteme.h5', 'subdir/subdir/deleteme.h5'),
    'group1k.h5': ('.', 'group1k_updated.h5'),
    'attr1k.h5': ('.',),
    'type1k.h5': ('.',),
    'fillvalue.h5': ('.'),
    'null_space_dset.h5': ('.'),
    'compound.h5': ('.',),
    'compound_attr.h5': ('.',),
    'compound_committed.h5': ('.',),
    'arraytype.h5': ('.',),
    'array_attr.h5': ('.',),
    'array_dset.h5': ('.',),
    'bitfield_attr.h5': ('.',),
    'bitfield_dset.h5': ('.',),
    'enum_attr.h5': ('.',),
    'enum_dset.h5': ('.',),
    'fixed_string_attr.h5': ('.',),
    'fixed_string_dset.h5': ('.',),
    'objref_attr.h5': ('.',),
    'objref_dset.h5': ('.',),
    'null_objref_dset.h5': ('.',),
    'regionref_attr.h5': ('.',),
    'regionref_dset.h5': ('.',),    
    'vlen_attr.h5': ('.',),
    'vlen_dset.h5': ('.',),
    'vlen_string_attr.h5': ('.',),
    'vlen_string_dset.h5': ('.',),
    'opaque_attr.h5': ('.',),
    'opaque_dset.h5': ('.',),
    'committed_type.h5': ('.',),
    'tstr.h5': ('.',)
}

# files that will get set as read-only
read_only_files = ( 'tall_ro.h5', 'readonly.h5')

"""
Make a testfile with 1000 sub-groups
"""
def makeGroup1k():
    file_path = SRC + "/group1k.h5"
    if os.path.exists(file_path):
        return # don't waste time re-creating
    print 'makeGroup1k'
    f = h5py.File(file_path, "w")
    for i in range(1000):
        name = 'g{:04d}'.format(i)
        f.create_group(name)
    f.close()
 
"""
Make a testfile with 1000 attributes
"""
def makeAttr1k():
    file_path = SRC + "/attr1k.h5" 
    if os.path.exists(file_path):
        return # don't waste time re-creating  
    print 'makeAttr1k()' 
    f = h5py.File(file_path, "w")
    for i in range(1000):
        name = 'a{:04d}'.format(i)
        f.attrs[name] = "this is attribute: " + str(i)
    f.close()
    
"""
Make a testfile with 1000 types
"""
def makeType1k():
    print "type!"
    file_path = SRC + "/type1k.h5" 
    print file_path
    if os.path.exists(file_path):
        return # don't waste time re-creating  
    print 'makeType1k()' 
    f = h5py.File(file_path, "w")
    for i in range(1000):
        name = 'S{:04d}'.format(i+1)
        f[name] = np.dtype(name)  #create fixed length string
    f.close()

"""
Remove files from given directory
"""    
def removeFilesFromDir(dir_name):
    print 'remove files', dir_name
    if not os.path.isdir(dir_name):
        print "expected", dir_name, "to be a directory"
        sys.exit()
    for file_name in os.listdir(dir_name):
        file_path = os.path.join(dir_name, file_name)
        try:
            if os.path.isdir(file_path):
                removeFilesFromDir(file_path)
                os.rmdir(file_path)
            else:
                if os.path.isfile(file_path):
                    # check for read-only
                    if (os.stat(file_path).st_mode & stat.S_IWUSR) == 0:
                        # make read-write
                        os.chmod(file_path, 0666)
                    os.unlink(file_path)
        except Exception, e:
            print e
    
"""
main
"""
# verify we are in the right place and the correct argument has been passed
if len(sys.argv) > 1 and sys.argv[1] == '-h':
    print "this script will remove all files from ../../data/test and repopulate using files from ../../testdata"
    sys.exit(); 
    
if not os.path.exists(SRC):
    print "run this from the integ test directory!"
    sys.exit()
    
if not  os.path.exists(DES):
    # create the data/test directory if it doesn't exist
    os.mkdir(DES)
    
# create group1k.h5 (if not created before)
makeGroup1k()

# create attr1k.h5 (if not created before)
makeAttr1k()

# create type1k.h5 (if not created before)
makeType1k()

removeFilesFromDir(DES)

test_dirs = ('.', 'subdir', 'subdir/subdir')
for dir_name in test_dirs:
    tgt_dir = DES
    if dir_name != '.':
        tgt_dir += '/' + dir_name
    if not os.path.exists(tgt_dir):
        os.mkdir(tgt_dir)
  
for file_name in testfiles:
    for tgt in testfiles[file_name]:
        src = SRC + '/' + file_name
        des = DES + '/'
        if tgt == '.':
            # copy to DES
            des += file_name
        else:
            des += tgt
            if os.path.isdir(des):
                # copy to directory
                des += '/'
                des += file_name
            
        print 'copyfile("'+file_name+'", "'+des+'")'    
        copyfile(src, des) 
        
for file_name in read_only_files:
    file_path = DES + '/' + file_name
    print 'chmod', file_path
    os.chmod(file_path, 0444)

    



