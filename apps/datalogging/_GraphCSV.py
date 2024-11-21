# File name: 
__name__ = 'GraphCSV'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 25 February 2020
# Date last modified: 27 February 2020
# Version 1.2
# MicroPython Version: 1.12 for the Kookaberry V4-05
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
# To the fullest extent permitted by law, AustSTEM absolutely disclaims 
# all warranties, expressed or implied, including, but not limited to, 
# implied warranties of merchantability and fitness for any particular purpose. 
# AustSTEM gives no warranty that this software will be free of errors, 
# or that defects in the software will be corrected,  
# See the GNU General Public License for more details.
#
# Description
# Lists CSV files in the root directory (as chosen) of the Kookaberry's serial memory
# User selects a file and then can convert it to a html chart file
# The html file requires JavaScript libraries stored on the Kookaberry as below
# The CSV data is presumed to have categories in column 1, then numerical data.
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: Nil
# /lib files: Nil
# /root files: Nil
# Other dependencies: in folder /c3d3/ files c3.css, c3.min.js, d3.min.js
# Complementary apps: Nil
#------------------------------------------

# Begin code
import kooka, machine, fonts, os, re, json, time

# Initial conditions
tx_dirs = ['/']    # list directories being read from
tx_dptr = 0
tx_fptr = 0    # pointer to the list of files
tx_files = []    # array of files in the current directory
tx_types = ['csv']    # file types eligible to be converted
maxrows = 28    # maximum number of data rows to import
g_ptr = 0    # pointer to the list of directories
g_types = ['line','spline','step','area','area-spline','area-step','bar','scatter','pie','donut','gauge']

# set up the objects
p = re.compile(r'\W+')     # regular expression to split strings into alphanumeric words
disp = kooka.display

# Function to fetch a cleaned up list of files in the named directory
def listdir(dir):
    olist = []
    flist = os.listdir(dir)    # fetch the full list
    for i in range(0,len(flist)):    # examine each entry
        entry = p.split(flist[i],3)    # split the entry
        if len(entry) == 2 and len(entry[0]) > 0 and len(entry[1]) > 0:
            if entry[1].lower() in tx_types:
                olist.append(flist[i])     # add to valid file list
    olist.sort()       
    return olist

# Populate the file list
tx_files = listdir(tx_dirs[tx_dptr])


# The main loop begins here
while not kooka.button_a.was_pressed():
# Display the static text
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('Fld=%s' % tx_dirs[tx_dptr], 80, 6)
    disp.text('A-x C-nx D-typ B-gph', 0, 60)
# Display the first three files
    for i in range(0,min(3,len(tx_files))):
        dl_ptr = i+tx_fptr
        if dl_ptr >= len(tx_files): dl_ptr -= len(tx_files)
        disp.text('%s' % tx_files[dl_ptr], 10, 20+10*i)
    disp.text('>', 0, 20)
# Adjust the parameters using the C and D keys
    if kooka.button_c.was_pressed(): # scroll to next file (circular)
        tx_fptr += 1
        if tx_fptr >= len(tx_files): tx_fptr = 0
    if kooka.button_d.was_pressed(): # select the graph type
        g_ptr += 1
        if g_ptr >= len(g_types): g_ptr = 0
    disp.text('%s:' % g_types[g_ptr], 0, 50)
    if kooka.button_b.was_pressed(): # Convert the file
# Read the csv file and transfer into an equivalent html file
        f_record = 1
        fname = tx_dirs[tx_dptr] + '/' + tx_files[tx_fptr]
        print(fname)
#        disp.setfont(fonts.mono5x5)
        disp.text('%s' % fname.lstrip('/'), len(g_types[g_ptr])*7+2, 50)
        disp.show()
        f = open(fname, 'r')
# Output the data into a html file utilising the c3.js graphing library
        hname = tx_files[tx_fptr].split('.')    # split the filename
        fh = open(hname[0]+'.htm','w+')
        fh.write('<html><head>\n')
        fh.write('<link rel="stylesheet" type="text/css" href="c3d3/c3.css">\n')
        fh.write('</head><h2>Graph of %s</h2><body><div id="chart"></div>\n' % tx_files[tx_fptr])
        fh.write('<script src="c3d3/d3.min.js" charset="utf-8"></script>\n')
        fh.write('<script src="c3d3/c3.min.js"></script>\n')
        fh.write('<script>\n')
        fh.write('var chart = c3.generate({\n')
        fh.write('data: {\n')
        fh.write('rows: [\n')
        no_rows=0 #used to find out the number of rows in the file
        for line in f:
            line=line.rstrip('\n')
            line=line.rstrip('\r')
            series = line.split(',')
            if no_rows == 0: xitem = series[0]
            curline = ''
            for item in series: 
                if item.isdigit(): curline = curline + item + ','
                else: curline = curline + ("'%s'," % item)
                line = curline.rstrip(',')
            fh.write('[%s],\n' % line)
            print(line)
            no_rows+=1
        no_cols = len(series)
        print(no_rows,no_cols)
        f.close()
        fh.write("],\nx: '%s',\ntype: '%s'\n},\n" % (xitem,g_types[g_ptr]))
        fh.write("axis: { x: {type: 'category',tick: { rotate: 90, multiline: false }, label: '%s' }},\n" % xitem)

        fh.write('onclick: function (d, element) { console.log("onclick", d, element); },\n')
        fh.write('onmouseover: function (d) { console.log("onmouseover", d); },\n')
        fh.write('onmouseout: function (d) { console.log("onmouseout", d); },\n')
        fh.write('});\n')
        fh.write('</script></body></html>\n')
        fh.close()
        
    disp.show()

# Clean up and exit


