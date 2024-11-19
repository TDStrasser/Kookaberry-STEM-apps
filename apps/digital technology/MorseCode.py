# FILENAME: MorseCode.py
__name__ = 'MorseCode'
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 20 April 2022
# DATE-MODIFIED: 15 May 2022 - squared up the signal graphs
# VERSION: 1.1
# SCRIPT: 1.12 for the Kookaberry V4-05
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
# A Morse Code demonstrator, encoder and decoder
# There are three modes:
#    1. The values of the alphanumeric Morse Codes are shown
#    2. Messages stored as text are encoded and sent as Morse Code
#    3. Messages received from another Morse Code app are decoded and shown as text.
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: P1 morse code digital input, P2 morse code digital output
# /lib files: Nil
# /root files: Nil
# Other dependencies: Nil
# Complementary apps: Nil
#------------------------------------------
# TAGS: #codes #cypher #morse #telegraph
# BEGIN-CODE:

import machine, kooka, fonts, random, time

pin_tx = 'P1'    # morse code digital output
pin_rx = 'P2'    # morese code digital input

disp = kooka.display

# Set up mode display strings
mode_ptr = 0
modes = [' Msg','  Tx','  Rx','Code']
controls = ['Nxt  Snd','Char  Nxt','Send','Clr  Nxt']
mode_max = len(modes)

# Morse Code arrays and conversions
characters = ['_','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5','6','7','8','9']
codes = ['/','01','1000','1010','100','0','0010','110','0000','00','0111','101','0100','11','10','111','0110','1101','010','000','1','001','0001','011','1001','1011','1100','11111','01111','00111','00011','00001','00000','10000','11000','11100','11110']
len_chars = len(characters) - 1

def list_to_dict(key_list, value_list):
    my_dict = {}
    for i in range (0, len(key_list)):
        my_dict[key_list[i]] = value_list[i]
    return my_dict
    
morse_encode_dict = list_to_dict(characters, codes)
morse_decode_dict = list_to_dict(codes, characters)

def code_to_string(code):
    disp_str = ''
    for char in code:
        if char == '/':
            disp_str += '/'
        elif char == '0':
            disp_str += '.'
        else:
            disp_str += '-'
    return disp_str
    
signal_out = machine.Pin(pin_tx, machine.Pin.OUT)    # create the digital output
signal_in = machine.Pin(pin_rx, machine.Pin.IN, machine.Pin.PULL_DOWN)    # create digital input 
dit_time = 100    # duration in msec of Morse Code dit
rx_sig = [0]*50
tx_sig = [0]*50
tx_buf = []
tx_flag = False

def code_tx(code):    # Sends code characters to the specified output
    global dit_time, signal_out, tx_flag
    vals = [0,0]    # [output, dits]
    for char in code:
        if char == '/': # inter-word space is silence for 7 (4 + 1 +2) dits
            vals = [0, 4]
        elif char == '0':    # dot for 1 dit
            vals = [1,1]
        elif char == '1':    # dash for 3 dits
            vals = [1,3]
        tx_buf.append(vals)    #queue for transmission
        # finish with silence for 1 dit
        tx_buf.append([0,1])
    # finish letter with 2 dit spaces
    tx_buf.append([0,2])
    tx_flag = True    # signal that transmission is pending    
        
# Set up interrupts so Kookaberry LEDs track the output and input pins
last_on = 0
last_off = 0
last_in = 0
rx_buf = []
char_buf = ''

def service_io(led_timer):
    global signal_out, signal_in, dit_time
    global last_on, last_off, last_in, rx_buf, char_buf
    global rx_sigs, tx_sigs, tx_buf, tx_flag
    
    # first send any signals that are queued
    if tx_buf:    # something to be sent
        if tx_buf[0][1] > 0: # signal time still current
            signal_out.value(tx_buf[0][0]) # set the signal
            tx_buf[0][1] -= 1 # decrement the timer
        else:
            tx_buf.pop(0)    # delete the item if timer is expired
    else:
        tx_flag = False
    
    tx_sig.append(signal_out.value())    # record transmit signal
    tx_sig.pop(0)    # delete the oldest one
    rx_sig.append(signal_in.value())    # record transmit signal
    rx_sig.pop(0)    # delete the oldest one
    
    if tx_sig[-1]: kooka.led_red.on()
    else: kooka.led_red.off()
    
    if rx_sig[-1]: # input is 1
        kooka.led_green.on()
        if not last_in: 
            last_on = time.ticks_ms()
            last_in = 1
            off_dits = round(time.ticks_diff(last_on, last_off) / dit_time, 0)
            if off_dits >= 7: # space between words
                char_buf = ''
                rx_buf.append('/')
            elif off_dits >= 3: # space between letters
                rx_buf.append(char_buf)
                while len(rx_buf) > 50: rx_buf.pop(0) # Limit characters held
                char_buf = ''
#            print(off_dits, char_buf, rx_buf)
        
    else: # input is 0
        kooka.led_green.off()
        if last_in:
            last_off = time.ticks_ms()
            last_in = 0
            on_dits = round(time.ticks_diff(last_off, last_on) / dit_time, 0)
            if on_dits >= 3: char_buf += '1' # dash received
            elif on_dits >= 1: char_buf += '0'
        elif char_buf: # character at end of transmission
            off_dits = round(time.ticks_diff(time.ticks_ms(),last_off) / dit_time, 0)
            if off_dits >= 8: # end of transmission
                rx_buf.append(char_buf)
                char_buf = ''
#            print(off_dits, char_buf)

led_timer = machine.Timer(-1, freq=int(1000/dit_time), callback=service_io)    # Set interrupt at dit time intervals

snd_msg = False

random.seed(time.ticks_ms())    # seed the random number generator using the time
char_ptr = random.randint(0,len(characters)-1)

# Text message for transmission'
txt_msg = 'Hello_World'.upper()    # the text
txt_lst = []
txt_lst.extend(txt_msg)    # convert text to list
txt_csr = '^'    # the current letter cursor
code_str = ''
for char in txt_lst:
    code_str += code_to_string(morse_encode_dict[char]) + ' '

# The main loop begins here
while not kooka.button_a.was_pressed():
# Display the static text
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text(__name__, 0, 6)
    disp.setfont(fonts.mono6x7)
    disp.text('X', 0, 63)
    disp.text('%s' % modes[mode_ptr], 100, 63)
    disp.text('%s' % controls[mode_ptr], 30, 63)
    disp.setfont(fonts.mono5x5)
    disp.text('Rx %s Tx %s' % (pin_rx,pin_tx), 80, 6)
# Change the mode of operation
    if kooka.button_b.was_pressed(): 
        mode_ptr += 1
        if mode_ptr == mode_max: mode_ptr = 0
        txt_ptr = 0    # reset pointer to text message

# Adjust the numbers according to the mode using the C and D keys
    if kooka.button_c.was_pressed():
        if mode_ptr == 0:
            char_ptr += 1
            if char_ptr > len_chars: char_ptr = 0
            
        elif mode_ptr == 1:    # Change current character in text message
            char_ptr = characters.index(txt_lst[txt_ptr]) # start at current character
            char_ptr += 1
            if char_ptr > len_chars: char_ptr = 0
            txt_lst[txt_ptr] = characters[char_ptr]
            txt_msg = ''
            code_str = ''
            for char in txt_lst: 
                txt_msg += char    # Reconstruct message string
                code_str += code_to_string(morse_encode_dict[char])

        elif mode_ptr == 2:    # Transmit text as Morse Code
            snd_msg = True
            txt_ptr = -1
            
        elif mode_ptr == 3:    # Move cursor on received text
            rx_buf = []
            char_buf = ''
            
    if kooka.button_d.was_pressed():
        if mode_ptr == 0: # Send the character as Morse Code
            code = morse_encode_dict[characters[char_ptr]]
            code_tx(code)
        elif mode_ptr == 1:    # Move to next character in text message
            txt_ptr += 1
            if txt_ptr >= len(txt_msg): txt_ptr = 0
        elif mode_ptr == 3: # Move to next character in received text
            txt_ptr += 1
            if txt_ptr >= len(rx_buf): txt_ptr = 0

# Transmit current text message
    if snd_msg and mode_ptr == 2 and not tx_flag:
        txt_ptr += 1
        if txt_ptr >= len(txt_msg): 
            txt_ptr = 0
            snd_msg = False
        else:
            code = morse_encode_dict[txt_lst[txt_ptr]]
            code_tx(code)
                    
# Display the results
    # Draw the rx and tx signal plots
    disp.setfont(fonts.mono5x5)
    disp.text('Rx', 10, 45)
    disp.text('Tx', 10, 53)
    disp_y = 45
    for i in range(0, len(rx_sig)-1):    # the record of rx signals
        disp.fill_rect(20+2*i, disp_y-5*rx_sig[i+1], 2, 1+5*rx_sig[i+1], 1)
    disp_y = 53
    for i in range(0, len(tx_sig)-1):    # the record of tx signals
        disp.fill_rect(20+2*i, disp_y-5*tx_sig[i+1], 2, 1+5*tx_sig[i+1], 1)
    
    if mode_ptr == 0:    # Show the character and code
        disp.setfont(fonts.mono6x7)
        disp.text('Char  Morse Code', 0, 15)
        disp.setfont(fonts.sans12)
        disp.text('%s' % characters[char_ptr], 10, 35)
        disp.text('%s' % code_to_string(morse_encode_dict[characters[char_ptr]]), 50, 35)
    elif mode_ptr in (1,2): # Show the text message and cursor
        disp.setfont(fonts.mono6x7)
        disp.text(txt_msg, 0, 15)
        disp.text(txt_csr, int(txt_ptr * 7), 25)
        disp.setfont(fonts.sans12)
        disp.text('%s' % code_to_string(morse_encode_dict[txt_lst[txt_ptr]]), int(txt_ptr * 7), 35)
    elif mode_ptr == 3: # show the receive buffer
        disp.setfont(fonts.mono6x7)
        code_str = ''
        rx_str = ''
        if len(rx_buf): # only if there is receive text
            for char in rx_buf: 
                if char in codes: 
                    code_str += char    # Reconstruct the code string filtering out invalid characters
                    rx_str += morse_decode_dict[char]
            start_char = max(0, txt_ptr-10)
            disp.text(rx_str[start_char:], 0, 15)
            disp.text(txt_csr, int((txt_ptr-start_char) * 7), 25)
            disp.setfont(fonts.sans12)
            disp.text('%s' % code_to_string(rx_buf[txt_ptr]), int((txt_ptr-start_char) * 7), 40)

    disp.show()
# Exit
led_timer.deinit()
