#!/usr/bin/env python

import os
import optparse
from traj import MeasurementsTable
from glob import glob


def meas2mat(filename,outfilename='',label='_meas'):

  # Determine files input
  if isinstance(filename, basestring):
      filename = [filename]
  for name in filename:
    if os.path.isdir(name):        # directory input
      temp = glob(os.path.join(name,"*.measurements")) # find matching files
      filename = filename + temp   # append to list of files
      filename.remove(name)        # remove directory
    
  # Determine output files
  if not outfilename:
    changeext = lambda nm: os.path.splitext(nm)[0]+"%s.mat"%label # function to change extensions
    outfilename = [changeext(name) for name in filename]          # change extensions
  elif isinstance(outfilename, basestring):
    if os.path.isdir(outfilename):    # output directory input
      outdir = outfilename
      getfilename = lambda nm: os.path.split(os.path.splitext(nm)[0])[1]           # function to get basename
      setfilename = lambda nm: os.path.join(outdir,getfilename(nm)+"%s.mat"%label) # function to set filename
      outfilename = [setfilename(name) for name in filename] # change filenames
    else:                             # filename input
      outfilename = [outfilename]
  
  for inname, outname in zip(filename, outfilename):
    try:
      M = MeasurementsTable(str(inname))
      M.save_to_matlab_file(outname)
    except:
      print("Conversion of %s failed!"%inname)

  return(outfilename)


if __name__ == '__main__':
  parser = optparse.OptionParser()
  parser.add_option("-o","--output",
                    help    = "The directory to which output will be saved [default: input directory]",
                    dest    = "outfilename",
                    action  = "store",
                    type    = "string",
                    default = "")
  parser.add_option("-l","--label",
                    help    = "The string to append to the basename in the output filename",
                    dest    = "label",
                    action  = "store",
                    type    = "string",
                    default = "_meas")

  options,args = parser.parse_args()

  if len(args)==0:
    parser.error("File or path required")

  if options.outfilename:
    assert( os.path.isdir( options.outfilename ) )

  meas2mat(args[0], **options.__dict__ )

