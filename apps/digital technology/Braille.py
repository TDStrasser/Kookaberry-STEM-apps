# FILENAME: Braille.py
__name__ = 'Braille'
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 23 April 2022
# DATE-MODIFIED: 9 May 2022
# Version 1.0
# SCRIPT: MicroPython Version: 1.12 for the Kookaberry V4-05
# LICENCE: This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.
# To the fullest extent permitted by law, AustSTEM absolutely disclaims 
# all warranties, expressed or implied, including, but not limited to, 
# implied warranties of merchantability and fitness for any particular purpose. 
# AustSTEM gives no warranty that this software will be free of errors, 
# or that defects in the software will be corrected,  
# See the GNU General Public License for more details.
#
# DESCRIPTION:
# Displays the alphabet and the Braille equivalent
# Provides some training examples of Braille to convert back to text
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: Nil
# /lib files: Nil
# /root files: Nil
# Other dependencies: Nil
# Complementary apps: Nil
#------------------------------------------
# TAGS: #codes #cypher #braille
# BEGIN-CODE:
import kooka, fonts, random, time, framebuf
disp = kooka.display

# Set up mode display strings
mode_ptr = 0
modes = ['Wrd','Brl','Chr']
controls = ['- Char +','Pick Show','Pick Show']
mode_max = len(modes)

# Morse Code arrays and conversions
characters = [' ','!','"','#','$','%','&',"'",'(',')','*','+',',','-',
    '.','/','0','1','2','3','4','5','6','7','8','9',':',';','<','=','>','?','@',
    'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S',
    'T','U','V','W','X','Y','Z','[','\\',']','^','_'
    ]

codes = ['','2346','5','3456','1246','146','12346','3','12356','23456','16',
    '346','6','36','46','34','356','2','23','25','256','26','235','2356',
    '236','35','156','56','126','123456','345','1456','4','1','12','14',
    '145','15','124','1245','125','24','245','13','123','134','1345','135',
    '1234','12345','1235','234','2345','136','1236','2456','1346','13456',
    '1356','246','1256','12456','45','456']

len_chars = len(characters) - 1

def list_to_dict(key_list, value_list):
    my_dict = {}
    for i in range (0, len(key_list)):
        my_dict[key_list[i]] = value_list[i]
    return my_dict
    
braille_encode_dict = list_to_dict(characters, codes)
#braille_decode_dict = list_to_dict(codes, characters)

# Function produces a braille sprite
def braille_sprite(code):
    dots123 = 0x00
    if '1' in code: dots123 |= 0x03
    if '2' in code: dots123 |= 0x18
    if '3' in code: dots123 |= 0xc0
    dots456 = 00
    if '4' in code: dots456 |= 0x03
    if '5' in code: dots456 |= 0x18
    if '6' in code: dots456 |= 0xc0
#    print(hex(dots123),hex(dots456))
    return framebuf.FrameBuffer(bytearray([dots123,dots123,0x00,dots456,dots456]),5, 8, framebuf.MONO_VLSB)

# Function draws a large Braille symbol on the given framebuffer at given coordinates
def braille_framebuf(disp, x, y, code):
    dot_size = 4
    x_size = 2*dot_size + 3*(dot_size-1) + 3
    y_size = 3*dot_size + 4*(dot_size-1) + 4
    disp.rect(x, y, x_size, y_size, 1) # Draw the outline rectangle
    if '1' in code: disp.fill_rect(x+dot_size, y+dot_size, dot_size, dot_size, 1)
    if '2' in code: disp.fill_rect(x+dot_size, y+3*dot_size, dot_size, dot_size, 1)
    if '3' in code: disp.fill_rect(x+dot_size, y+5*dot_size, dot_size, dot_size, 1)
    if '4' in code: disp.fill_rect(x+3*dot_size, y+dot_size, dot_size, dot_size, 1)
    if '5' in code: disp.fill_rect(x+3*dot_size, y+3*dot_size, dot_size, dot_size, 1)
    if '6' in code: disp.fill_rect(x+3*dot_size, y+5*dot_size, dot_size, dot_size, 1)
    
# Function returns and array of codes corresponding to the text string
def text_to_braille(text):
    codes = []
    text = text.upper()    # convert all to upper case
    for char in text:
        codes.append(braille_encode_dict[char]) # look up braille
    return codes
    
# Array of common words for translation
words = ['to','be','the','big','small','low','high','open','shut',
    'door','window','boy','girl','father','mother','after','before',
    'stop','go','sit','stand','wait','now','hot','cold','exit','entry',
    'water','food','eat','run','cat','dog','cow','sheep','up','down',
    'look','learn','is','fun','kookaberry']

len_words = len(words) - 1

# Initialise the character to be shown
random.seed(time.ticks_ms())    # seed the random number generator using the time
char_ptr = random.randint(0,len_chars)
text = characters[char_ptr].upper()
codes = text_to_braille(text)
show_braille = show_text = 1

# The main loop begins here
while not kooka.button_a.was_pressed():
# Display the static text
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text(__name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('X', 0, 60)
    disp.text('%s' % modes[mode_ptr], 100, 60)
    disp.text('%s' % controls[mode_ptr], 30, 60)
# Change the mode of operation
    if kooka.button_b.was_pressed(): 
        mode_ptr += 1
        text = ''
        if mode_ptr == mode_max: 
            mode_ptr = 0
            char_ptr = random.randint(0,len_chars)
            text = characters[char_ptr].upper()
            show_braille = show_text = 1
        codes = text_to_braille(text)

# Adjust the display according to the mode using the C and D keys
    if kooka.button_c.was_pressed():
        if mode_ptr == 0:
            char_ptr -= 1
            if char_ptr < 0: char_ptr = len_chars
            text = characters[char_ptr].upper()
            codes = text_to_braille(text)
            show_braille = show_text = 1
        elif mode_ptr == 1:    # Random word, user solves  braille
            word_ptr = random.randint(0,len_words)
            text = words[word_ptr].upper()
            codes = text_to_braille(text)
            show_braille = 0
            show_text = 1
        else:    # Random braille, user solves text
            word_ptr = random.randint(0,len_words)
            text = words[word_ptr].upper()
            codes = text_to_braille(text)
            show_text = 0
            show_braille = 1
    if kooka.button_d.was_pressed():
        if mode_ptr == 0:
            char_ptr += 1
            if char_ptr > len_chars: char_ptr = 0
            text = characters[char_ptr].upper()
            codes = text_to_braille(text)
            show_braille = show_text = 1
        else: show_braille = show_text = 1

# Display the results
    if mode_ptr == 0: # Shows letter and Braille enlarged
        disp.setfont(fonts.sans12)
        disp.text(text, 20, 35)
        braille_framebuf(disp, 60, 15, codes[0])
        
    else:
        disp.setfont(fonts.mono8x8)
        if show_text: disp.text('%s' % text, 0, 18)
        disp.setfont(fonts.mono6x7)
        disp.text('Braille:', 0, 30)
        disp_x = 2
        if show_braille:
            for code in codes:
                disp.blit(braille_sprite(code),disp_x,38)
                disp.rect(disp_x-2,36,9,12,1)
                disp_x += 13
    disp.show()
