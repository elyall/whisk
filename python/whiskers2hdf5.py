#!/usr/bin/env python
"""
Convert .whiskers files generated from nclack's whisk to .hdf5 using code from cxrodgers.
"""

import os
import optparse
import numpy as np
import tables
from glob import glob
try:
    from whisk.python import trace
except ImportError:
    print "cannot import whisk"


def setup_hdf5(h5_filename, expectedrows):

    # Open file
    h5file = tables.open_file(h5_filename, mode="w")    
    
    
    # A group for the normal data
    table = h5file.create_table(h5file.root, "summary", WhiskerSeg, 
        "Summary data about each whisker segment",
        expectedrows=expectedrows)

    # Put the contour here
    xpixels_vlarray = h5file.create_vlarray(
        h5file.root, 'pixels_x', 
        tables.Float32Atom(shape=()),
        title='Every pixel of each whisker (x-coordinate)',
        expectedrows=expectedrows)
    ypixels_vlarray = h5file.create_vlarray(
        h5file.root, 'pixels_y', 
        tables.Float32Atom(shape=()),
        title='Every pixel of each whisker (y-coordinate)',
        expectedrows=expectedrows)
    
    h5file.close()
    

def append_whiskers_to_hdf5(whisk_filename, h5_filename='', label='', permission='a'):
    """Load data from whisk_file and put it into an hdf5 file
    
    The HDF5 file will have two basic components:
        /summary : A table with the following columns:
            time, id, fol_x, fol_y, tip_x, tip_y, pixlen
            These are all directly taken from the whisk file
        /pixels_x : A vlarray of the same length as summary but with the
            entire array of x-coordinates of each segment.
        /pixels_y : Same but for y-coordinates
    """
    
    # Determine files input
    if isinstance(whisk_filename, basestring):
        whisk_filename = [whisk_filename]
    for name in whisk_filename:
        if os.path.exists(os.path.dirname(name)):        # if directory input
            temp = glob(os.path.join(name,"*.whiskers")) # find matching files
            whisk_filename = whisk_filename + temp       # append to list of files
            whisk_filename.remove(name)                  # remove directory
    
    # Determine output files
    if not h5_filename:
        changeext = lambda nm: os.path.splitext(nm)[0]+"%s.hdf5"%label # function to change extensions
        h5_filename = [changeext(name) for name in whisk_filename]     # change extensions
    elif isinstance(h5_filename, basestring):
        if os.path.exists(os.path.dirname(h5_filename)):      # output directory input
            outdir = h5_filename
            getfilename = lambda nm: os.path.split(os.path.splitext(nm)[0])[1] # function to get filename
            setfilename = lambda nm: os.path.join(outdir,getfilename(nm)+"%s.hdf5"%label) # function to set filename
            h5_filename = [setfilename(name) for name in whisk_filename] # change filenames
        else:                                          # filename input
            h5_filename = [h5_filename]
    if not len(h5_filename) == len(whisk_filename):
        h5_filename = [h5_filename[0]]*len(whisk_filename) # set equal in length to input files

    # Iterate over input files
    for inname, outname in zip(whisk_filename, h5_filename):

        ## Load it, so we know what expectedrows is
        # This loads all whisker info into C data types
        # wv is like an array of trace.LP_cWhisker_Seg
        # Each entry is a trace.cWhisker_Seg and can be converted to
        # a python object via: wseg = trace.Whisker_Seg(wv[idx])
        # The python object responds to .time and .id (integers) and .x and .y (numpy
        # float arrays).
        #wv, nwhisk = trace.Debug_Load_Whiskers(whisk_filename)
        whiskers = trace.Load_Whiskers(inname)
        nwhisk = np.sum(map(len, whiskers.values()))

        # Create file if it doesn't exist
        if not os.path.exists(outname) or permission=='w':
            setup_hdf5(outname,nwhisk)
        
        # Open file
        h5file = tables.open_file(outname, mode="a")

        ## Iterate over rows and store
        table = h5file.get_node('/summary')
        h5seg = table.row
        xpixels_vlarray = h5file.get_node('/pixels_x')
        ypixels_vlarray = h5file.get_node('/pixels_y')
        for frame, frame_whiskers in whiskers.iteritems():
            for whisker_id, wseg in frame_whiskers.iteritems():
                # Write to the table
                # h5seg['chunk_start'] = chunk_start
                h5seg['time'] = wseg.time # + chunk_start
                h5seg['id'] = wseg.id
                h5seg['fol_x'] = wseg.x[0]
                h5seg['fol_y'] = wseg.y[0]
                h5seg['tip_x'] = wseg.x[-1]
                h5seg['tip_y'] = wseg.y[-1]
                h5seg['pixlen'] = len(wseg.x)
                assert len(wseg.x) == len(wseg.y)
                h5seg.append()
            
                # Write x
                xpixels_vlarray.append(wseg.x)
                ypixels_vlarray.append(wseg.y)

        table.flush()
        h5file.close()

    return h5_filename


class WhiskerSeg(tables.IsDescription):
    time = tables.UInt32Col()
    id = tables.UInt16Col()
    tip_x = tables.Float32Col()
    tip_y = tables.Float32Col()
    fol_x = tables.Float32Col()
    fol_y = tables.Float32Col()
    pixlen = tables.UInt16Col()
    # chunk_start = tables.UInt32Col()


if __name__ == '__main__':
  parser = optparse.OptionParser()
  parser.add_option("-o","--output",
                    help    = "The directory to which output will be saved [default: input directory]",
                    dest    = "h5_filename",
                    action  = "store",
                    type    = "string",
                    default = "")

  options,args = parser.parse_args()

  if len(args)==0:
    parser.error("Path to movie files required")

  assert( os.path.isdir( args[0] ) )
  if options.h5_filename:
    assert( os.path.isdir( options.h5_filename ) )

  append_whiskers_to_hdf5(args[0], **options.__dict__ )

