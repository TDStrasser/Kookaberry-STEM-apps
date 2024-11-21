# File name: Fractions101.py
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 21 February 2019
# Date last modified: 4 December 2020
# Version 1.2
# MicroPython Version: 1.12 for the Kookaberry V4-06
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
# App to display proper fractions and to compare their relative sizes
# Added mode to add and subtract fractions and their decimal equivalents
# Begin code

# Euclid's algorithm to find the lowest common denominator
# This is used to reduce the size of the denominator in the maths results
def gcd(a, b):
  while b:
    a, b = b, a % b
  return a

import machine, kooka, fonts, time
# set up the fractions to be used
denom_vals = [2, 3, 4, 5, 6, 8, 10, 12]    # From Stage 3 curriculum
denom_ptrs = [1,1]
denominators = [2]*2
numerators = [1]*2
den_len = len(denom_vals)
result_den = 0
result_num = [0,0]
numerators_mem = [1]*2
# set up the control modes
modes = ['Den1','Num1','Den2','Num2','Math','Back']
cbtn = ['Dn','Dn','Dn','Dn','-','']
dbtn = ['Up','Up','Up','Up','+','']
mode_ptr = 0
# set up the fractions display bars
frac_y = [15,35]
frac_h = 10
frac_x = 32
frac_w = int(127-2*frac_x)
disp = kooka.display
# The main loop begins here
while not kooka.button_a.was_pressed():
# Display the static text
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('Fractions101', 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('Ex', 0, 60)
    disp.text('%s' % cbtn[mode_ptr], 40, 60)
    disp.text('%s' % dbtn[mode_ptr], 70, 60)
    disp.text('%s' % modes[mode_ptr], 95, 60)
    disp.setfont(fonts.mono6x7)    # for fractions text display
    # update the denominators and numerators
    for i in range(0,2):
         denominators[i] = denom_vals[denom_ptrs[i]]
         numerators[i] = min(numerators[i],denominators[i])
         if mode_ptr == 5:    # if displaying result of maths
             denominators[i] = result_den
             numerators[i] = result_num[i]

    for i in range(0,2):    # display numerical fractions
        disp.text('%2d/%d' % (numerators[i],denominators[i]), 0, frac_y[i]+8)
        disp.text('%0.2f' % (numerators[i]/denominators[i]),100, frac_y[i]+8)
    if mode_ptr == 5: 
        disp.text('%d/%d=%0.2f' % (result,result_den,result/result_den), 20,60)
    # Adjust the parameters using the C and D keys
    if kooka.button_c.was_pressed(): 
        if mode_ptr == 0: denom_ptrs[0] = max(0, denom_ptrs[0]-1)
        elif mode_ptr == 1: numerators[0] = max(0, numerators[0]-1)
        elif mode_ptr == 2: denom_ptrs[1] = max(0, denom_ptrs[1]-1)
        elif mode_ptr == 3: numerators[1] = max(0, numerators[1]-1)
        elif mode_ptr == 4:
            for i in range(0,2): numerators_mem[i] = numerators[i]    # memorise numerators
            result_den = denominators[0] * denominators[1]
            result = abs(numerators[0]*denominators[1]-numerators[1]*denominators[0])
#            print(result, result_den)
            lcd = gcd(result,result_den)    # find the lowest common denominator
            if lcd:
                result_den = int(result_den/lcd)
                result = int(result/lcd)
#                print('..',result,result_den)
            result_num[0] = min(result_den,result)
            result_num[1] = max(0,result-result_num[0])
#            print(result, result_den)
            mode_ptr = 5
    if kooka.button_d.was_pressed(): 
        if mode_ptr == 0: denom_ptrs[0] = min(den_len-1, denom_ptrs[0]+1)
        elif mode_ptr == 1: numerators[0] = min(denom_vals[denom_ptrs[0]], numerators[0]+1)
        elif mode_ptr == 2: denom_ptrs[1] = min(den_len-1, denom_ptrs[1]+1)
        elif mode_ptr == 3: numerators[1] = min(denom_vals[denom_ptrs[1]], numerators[1]+1)
        elif mode_ptr == 4:
            for i in range(0,2): numerators_mem[i] = numerators[i]    # memorise numerators
            result_den = denominators[0] * denominators[1]
            result = abs(numerators[0]*denominators[1]+numerators[1]*denominators[0])
#            print(result, result_den)
            lcd = gcd(result,result_den)    # find the lowest common denominator
            if lcd:
                result_den = int(result_den/lcd)
                result = int(result/lcd)
#                print('..',result,result_den)
            result_num[0] = min(result_den,result)
            result_num[1] = max(0,result-result_num[0])
#            print(result, result_den)
            mode_ptr = 5
    if kooka.button_b.was_pressed(): 
        if mode_ptr < 4:
            mode_ptr += 1
            if mode_ptr > len(modes)-1: mode_ptr = 0
        elif mode_ptr == 4: mode_ptr = 0
        elif mode_ptr == 5: 
            for i in range(0,2): numerators[i] = numerators_mem[i]
            mode_ptr = 4
    # Draw the fractions bars
    for j in range(0,2):
        disp.rect(frac_x,frac_y[j],frac_w,frac_h,1)    # draw outline rectangle
        disp.fill_rect(frac_x,frac_y[j],int(frac_w*numerators[j]/denominators[j]),frac_h,1)
        for i in range(0,denominators[j]):
            x = frac_x + int(i*(frac_w/denominators[j]))
            y = frac_y[j]
            disp.vline(x, y, frac_h, 1)

    disp.show()


