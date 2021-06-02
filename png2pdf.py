#!/usr/bin/env python3

#
# Time-stamp: <2021-06-02 17:11:13 nmaeda>
#

#
# Author
#
#  Kinoshita Daisuke
#
# History
#
#  version 1.0: 23/Mar/2021 by Kinoshita Daisuke
#  version 1.1: 25/Apr/2021 by Kinoshita Daisuke
#  version 1.2: 01/Jun/2021 by Kinoshita Daisuke
#

# importing argparse module
import argparse

# importing os module
import os

# importing sys module
import sys

# importing datetime module
import datetime

# importing pathlib module
import pathlib

# importing subprocess module
import subprocess

# command-line argument analysis
desc = 'Conversion from multiple PNG files into a single PDF file'
parser = argparse.ArgumentParser (description=desc)
parser.add_argument ('files', nargs='+', help='input PNG files')
parser.add_argument ('-o', '--output', default='test.pdf', \
                     help='output PDF file')
args = parser.parse_args ()

# file names
files_png         = args.files
file_pdf_combined = args.output

# commands
command_convert  = subprocess.run('which convert', shell=True, stdout=subprocess.PIPE, text=True).stdout
command_tiff2pdf = subprocess.run('which tiff2pdf', shell=True, stdout=subprocess.PIPE, text=True).stdout
command_gs       = subprocess.run('which gs', shell=True, stdout=subprocess.PIPE, text=True).stdout
option_tiff2pdf  = ''
option_gs        = '-dNOPAUSE -dBATCH -q -sDEVICE=pdfwrite'

# remove escape sequance
command_convert = command_convert.split("\n")[0]
command_tiff2pdf = command_tiff2pdf.split("\n")[0]
command_gs = command_gs.split("\n")[0]

# check of existence of commmands
path_convert = pathlib.Path (command_convert)
if not path_convert.is_file ():
    print ("The command \"%s\" does not exist." % command_convert)
    print ("Install graphics/ImageMagick on your computer!")
    sys.exit ()
path_tiff2pdf = pathlib.Path (command_tiff2pdf)
if not path_tiff2pdf.exists ():
    print ("The command \"%s\" does not exist." % command_tiff2pdf)
    print ("Install graphics/tiff on your computer!")
    sys.exit ()
path_gs = pathlib.Path (command_gs)
if not path_gs.exists ():
    print ("The command \"%s\" does not exist." % command_gs)
    print ("Install print/ghostscript on your computer!")
    sys.exit ()

# date/time
now = datetime.datetime.now ()
datetime_str = "%04d%02d%02d_%02d%02d%02d" \
    % (int (now.year), int (now.month), int (now.day), \
       int (now.hour), int (now.minute), int (now.second) )

# process ID
pid = os.getpid ()

# directories and files
dir_tmp = "/tmp/tmp_%s_%d" % (datetime_str, pid)

# making a directory
path_tmp = pathlib.Path (dir_tmp)
path_tmp.mkdir (parents=True, exist_ok=True)

# counter for number of PNG files
n_png = 0

# processing PNG files one-by-one
for file_png in files_png:
    # if not a PNG file, then skip
    if not (file_png[-4:] == '.png'):
        continue

    # file names
    file_tiff = dir_tmp + '/' + file_png[:-4] + '.tiff'
    file_pdf  = dir_tmp + '/' + file_png[:-4] + '.pdf'
    if (n_png == 0):
        files_pdf  = file_pdf
    else:
        files_pdf += " %s" % (file_pdf)
    
    # command to convert a single PNG file into TIFF file
    command_0_png2tiff = "%s %s %s" % (command_convert, file_png, file_tiff)

    # command to convert a single TIFF file into PDF file
    command_1_tiff2pdf = "%s %s -o %s %s" % (command_tiff2pdf, \
                                             option_tiff2pdf, \
                                             file_pdf, file_tiff)

    # executing a command to convert a single PNG file into TIFF file
    print (command_0_png2tiff)
    subprocess.run (command_0_png2tiff, shell=True)

    # executing a command to convert a single TIFF file into PDF file
    print (command_1_tiff2pdf)
    subprocess.run (command_1_tiff2pdf, shell=True)

    # incrementing the parameter "n_png"
    n_png += 1

# if there is no PDF file converted from PNG file, then stop the script.
if (n_png == 0):
    print ("There is no PNG file to convert.")
    print ("Stopping the script.")
    sys.exit ()

# command to combine multiple PDF files into a single PDF file
command_2_pdf2pdf = "%s %s -sOutputFile=%s %s" \
    % (command_gs, option_gs, file_pdf_combined, files_pdf)

# executing a command to combine multiple PDF files into a single PDF file
print (command_2_pdf2pdf)
subprocess.run (command_2_pdf2pdf, shell=True)
