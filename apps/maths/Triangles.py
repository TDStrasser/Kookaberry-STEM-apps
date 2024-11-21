# File name: 
__name__ = 'Triangles'
# Copyright: The AustSTEM Foundation Limited
# Author: Tony Strasser
# Date created: 7 December 2020
# Date last modified: 1 January 2021
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
"""
An informational and quiz app on the subject of triangles.
It provides graphical examples and then runs a short quiz using randomised
samples with multiple choice answers
It covers:
    Types of triangles - equilateral, isosceles, scalene
    Angles - sum to 180, acute, right angle, obtuse triangles
    Perimeter - sum of the sides
    Pythagoras' Theorem (not yet)
    Area of triangle - half height x width
"""
#------------------------------------------
# Dependencies:
# I/O ports and peripherals: Nil
# /lib files: Nil
# /root files: Nil
# Other dependencies: Nil
# Complementary apps: None
#------------------------------------------

# Begin code
import kooka, fonts, random
from display_triangle import triangle, equilateral, isosceles

# Initial conditions
disp = kooka.display
tr_size = [0, 10, 50, 40]    # Triangle display origin, width and height
txt_x = tr_size[0] + tr_size[2]+ 2
tr_names = ['Equilateral','Isosceles','Scalene','Acute','Right Angle','Obtuse']
typ_strings = ['3 eq sides','2 eq sides','0 eq sides','Angles < 90','1 angle 90','1 angle > 90']
# Table of triangle information - first field is info selector
tr_type = [(1,0,60,equilateral()), 
(1,1,63,isosceles(65)),
(1,1,73,isosceles(73)),
(1,1,80,isosceles(80)),
(1,2,100,0.6),
(2,3,50,1),
(2,3,60,1),
(2,3,70,1),
(2,3,80,1),
(2,4,90,1),
(2,4,90,0.6),
(2,4,45,1),
(2,5,100,0.6),
(2,5,110,0.6),
(2,5,56,0.6),
(2,5,50,0.6)]
        
# Begin main loop here
tr_disp = triangle(disp, tr_size)    # Initialise the triangle display object
tr_ptr = -1    # Initialise the triangle type pointer to null
stage = 0    # State machine indicator
scale = 1.0    # Scale factor for triangle dimensions
initialise = True    # Causes an initialisation of triangle parameters
tr_random = False    # If set causes a random triangle to be picked
questions = 0    # Number of questions asked in quizes
correct = 0    # Number of correct answers to qui questions
result = ""    # Variable contains the result text
b_strng = ['A-x C-nxt D-prv B-qz','A-x C-choose-D B-nxt']
btn_strings = [b_strng[0],b_strng[0], b_strng[1], b_strng[0],b_strng[1]]    # Menus at different stages
hdg_strings = ['Types','Type Qz','Angl Qz','Area','Area Qz']    # Titke strings for each stage
ans_strings = ['Incorrect', 'Correct']    # Result text options
# The main loop begins here
while not kooka.button_a.was_pressed():
    # Prepare the static display
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('%s' % __name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text(hdg_strings[stage], 80, 6)
    disp.text(btn_strings[stage], 0, 62)
    # Process button presses
    if kooka.button_b.was_pressed():    # Increment stage of info/quiz
        stage += 1
        scale = 1.0    # Reset dimensions scale to 1.0
        result = ""    # Reset the last response text
        if stage >= len(btn_strings): stage = 0
        if stage == 1 or stage == 3: tr_random = True        
    if stage == 0 or stage == 3:    # Informational pages
        if kooka.button_c.was_pressed() or initialise:    # Increment triangle description
            tr_ptr += 1
            initialise = False
            if tr_ptr >= len(tr_type): # If all types have been shown
                tr_ptr = 0    # Go back to beginning... and
                scale = 1 + random.random() * 4    # Scale triangles after first round
            update = True
        if kooka.button_d.was_pressed():    # Increment triangle description
            tr_ptr -= 1
            initialise = False
            if tr_ptr < 0: # Backed down to beginning
                tr_ptr = len(tr_type) - 1    # Go to last choice
                scale = 1.0    # Reset scale to 1
            update = True

    if stage in [1, 2, 4]:    # If a quiz
        if kooka.button_c.was_pressed():
            kooka.button_d.was_pressed()    # Invalidate other button
            questions += 1
            if stage == 1: eval = choice_c == choices[0] # identify quiz
            if stage == 2: eval = angle_c == ang_choices[0]    # angles quiz
            if stage == 4: eval = area_c == area    # area quiz
            result = ans_strings[eval]
            correct += eval
            tr_random = True
        if kooka.button_d.was_pressed():
            kooka.button_c.was_pressed()    # Invalidate other button
            questions += 1
            if stage == 1: eval = choice_d == choices[0] # identify quiz
            if stage == 2: eval = angle_d == ang_choices[0]    # angles quiz
            if stage == 4: eval = area_d == area    # area quiz
            result = ans_strings[eval]
            correct += eval
            tr_random = True
            

        if questions > 10 and correct / questions >= 0.8: scale = 1 + random.random() * 4    # Extend difficulty of quiz if score is above 80%
        else: scale = 1.0    # Reset scale to 1.0 for those struggling
            
    if tr_random:    # Choose a random triangle and another with a different name
        tr_ptr = random.randint(0,len(tr_type)-1)    # Choose a random triangle
        type = tr_type[tr_ptr]
        update = True    # Initialise the new triangle
        tr_random = False
        tr_other = random.randint(0, len(tr_type)-1)
        typ_other = tr_type[tr_other]
        while (tr_names[type[1]] == tr_names[typ_other[1]]) or (type[0] != typ_other[0]):    # Keep choosing until names are different and class the same
            tr_other = random.randint(0, len(tr_type)-1)
            typ_other = tr_type[tr_other]
#            print(tr_ptr, tr_type[tr_ptr][0], tr_other, tr_type[tr_other][0])
        choices = [tr_names[type[1]], tr_names[typ_other[1]]]
        rand_ptr = random.randint(0,1)
        choice_c = choices[rand_ptr]
        choice_d = choices[not rand_ptr]
        
    if update:
#        print(tr_type[tr_ptr])
        type = tr_type[tr_ptr]
        tr_disp.ratio(type[3])
        tr_disp.draw(type[2])
        angles = tr_disp.angles()
#        print('Angles ',angles)
        sides = tr_disp.sides()
        for i in range(0, len(sides)): sides[i] *= scale
#        print('Sides ', sides)
        height = 1.0 * scale
        area = height * sides[0] / 2
#        print('Height ', height)
        # Prepare randomised area choices for area quiz
        if random.randint(0,1): a_other = max(0.1, area * (0.1 + random.random() * 0.8))
        else: a_other = area * (1.5 + random.random() * 0.5)
        a_choices = [area, a_other]
        rand_ptr = random.randint(0,1)
        area_c = a_choices[rand_ptr]
        area_d = a_choices[not rand_ptr]
        # Prepare randomised angle choices for angle quiz
        ang_choices = [angles[0], max(5, sum(angles)/len(angles) - 10)]
        if int(ang_choices[1]) == int(ang_choices[0]): ang_choices[1] += 2
        angle_c = ang_choices[rand_ptr]
        angle_d = ang_choices[not rand_ptr]
        update = False
    # Display triangle type information
    if stage == 0:
        tr_disp.draw(type[2])
        disp.setfont(fonts.mono6x7)
        disp.text("%s" % tr_names[type[1]], txt_x, 15)
        disp.text("%s" % typ_strings[type[1]], txt_x, 24)
        if type[0] == 2:    # Angles Classes
            disp.text("Angles:", txt_x,33)
            disp.text("%2.0f %2.0f %2.0f" % (angles[0],angles[1],angles[2]), txt_x, 42)
            disp.text("Sum=180", txt_x, 51)
        if type[0] == 1: # Sides classes
            disp.text("Sides:", txt_x,33)
            disp.text("%0.1f %0.1f %0.1f" % (sides[0],sides[1],sides[2]), txt_x, 42)
        if tr_disp.constrained: disp.text("!", txt_x - 6, 42)    # If dimensions constrained
    # Conduct a quiz on recognising triangles
    if stage == 1:
        tr_disp.draw(type[2])
        disp.setfont(fonts.mono6x7)
        disp.text("Identify", txt_x, 15)
        disp.text("C:%s" % choice_c, txt_x, 24)
        disp.text("D:%s" % choice_d, txt_x, 33)

    # Conduct a quiz on triangle angles
    if stage == 2:
        tr_disp.draw(type[2])
        disp.setfont(fonts.mono6x7)
        disp.text("A1:%2.0f A2:%2.0f" % (angles[1], angles[2]), txt_x, 15)
        disp.text("A3 is?", txt_x, 24)
        disp.text("C:%2.0f D:%2.0f" % (angle_c, angle_d), txt_x, 33)

    # Provide information on calculating areas
    if stage == 3:
        tr_disp.draw(type[2], True)
        disp.setfont(fonts.mono6x7)
        disp.text("Area =", txt_x, 15)
        disp.text(" b x h / 2", txt_x, 24)
        disp.text("base:%0.1f" % sides[0], txt_x, 33)
        disp.text("height:%0.1f" % height, txt_x, 42)
        disp.text("Area:%0.1f" % area, txt_x, 51)
    # Conduct a quiz on area of triangles
    if stage == 4:
        tr_disp.draw(type[2], True)
        disp.setfont(fonts.mono6x7)
        disp.text("h:%0.1f b:%0.1f" % (height,sides[0]), txt_x, 15)
        disp.text("Area is?", txt_x, 24)
        disp.text("C:%0.1f D:%0.1f" % (area_c,area_d), txt_x, 33)
        
    if stage in [1, 2, 4]:
        disp.text("LQ: %s" % result, txt_x, 42)
        disp.text("Score:%d/%d" % (correct, questions), txt_x, 51)
        
    disp.show()

# Clean up and exit