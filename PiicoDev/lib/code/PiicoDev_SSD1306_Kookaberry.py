# FILENAME: PiicoDev_SSD1306_Kookaberry.py
# COPYRIGHT: The AustSTEM Foundation Limited
# AUTHOR: Tony Strasser
# DATE-CREATED: 19 August 2025
# DATE-MODIFIED: 
# VERSION: 1.0
# SCRIPT: MicroPython for Kookaberry Version: 1.24 for the Raspberry Pi Pico with RP2040 and RP2350
# LICENCE:
'''
Copyright 2020 Core Electronics Pty Ltd and 2025 The AustSTEM Foundation

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
#
# DESCRIPTION:
# Sends data to the Core Electronics PiicoDev OLED SSD1306 Display
# Ported by Peter Johnston at Core Electronics October 2021
# Original Repos:
# 2021-09-12:
# https://github.com/micropython/micropython/blob/master/drivers/display/ssd1306.py
# 2021-08-01:
# https://github.com/fizban99/microbit_ssd1306/blob/master/ssd1306_text.py
# 2021-07-15:
# https://github.com/adafruit/Adafruit_Python_SSD1306/blob/master/Adafruit_SSD1306/SSD1306.py

# 2021 OCT 14 - Initial release
# 2022 JAN 04 - Remove dependency on PIL module.  Improve compatibility with pbm files.

# 2025 AUG 18 - Modified for use by Kookaberry (only) by T.Strasser at AustSTEM
# Usage: https://github.com/CoreElectronics/CE-PiicoDev-SSD1306-MicroPython-Module/blob/main/README.md
# Differences: No dependency on the PiicoDev Unified Library - uses Kookaberry MicroPython firmware
#
#------------------------------------------
# DEPENDENCIES:
# I/O ports and peripherals: PiicoDev SSD1306 module connected to any I2C capable GPIOs
# /lib files: place this file or compiled .mpy in the /lib folder
# /root files: None
# Other dependencies:
# Complementary apps:
#------------------------------------------
# TAGS:
# BEGIN-CODE:

_SET_CONTRAST = 0x81
_SET_ENTIRE_ON = 0xA4
_SET_NORM_INV = 0xA6
_SET_DISP = 0xAE
_SET_MEM_ADDR = 0x20
_SET_COL_ADDR = 0x21
_SET_PAGE_ADDR = 0x22
_SET_DISP_START_LINE = 0x40
_SET_SEG_REMAP = 0xA0
_SET_MUX_RATIO = 0xA8
_SET_IREF_SELECT = 0xAD
_SET_COM_OUT_DIR = 0xC0
_SET_DISP_OFFSET = 0xD3
_SET_COM_PIN_CFG = 0xDA
_SET_DISP_CLK_DIV = 0xD5
_SET_PRECHARGE = 0xD9
_SET_VCOM_DESEL = 0xDB
_SET_CHARGE_PUMP = 0x8D
WIDTH = 128
HEIGHT = 64

from math import cos,sin,radians
from utime import sleep_ms
from ustruct import pack_into
import framebuf
    
    
class PiicoDev_SSD1306(framebuf.FrameBuffer):
    def init_display(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.pages = HEIGHT // 8
        self.buffer = bytearray(self.pages * WIDTH)
        for cmd in (
            _SET_DISP,  # display off
            # address setting
            _SET_MEM_ADDR,
            0x00,  # horizontal
            # resolution and layout
            _SET_DISP_START_LINE,  # start at line 0
            _SET_SEG_REMAP | 0x01,  # column addr 127 mapped to SEG0
            _SET_MUX_RATIO,
            HEIGHT - 1,
            _SET_COM_OUT_DIR | 0x08,  # scan from COM[N] to COM0
            _SET_DISP_OFFSET,
            0x00,
            _SET_COM_PIN_CFG,
            0x12,
            # timing and driving scheme
            _SET_DISP_CLK_DIV,
            0x80,
            _SET_PRECHARGE,
            0xF1,
            _SET_VCOM_DESEL,
            0x30,  # 0.83*Vcc
            # display
            _SET_CONTRAST,
            0xFF,# maximum
            _SET_ENTIRE_ON,  # output follows RAM contents
            _SET_NORM_INV,  # not inverted
            _SET_IREF_SELECT,
            0x30,  # enable internal IREF during display on
            # charge pump
            _SET_CHARGE_PUMP,
            0x14,
            _SET_DISP | 0x01,  # display on
        ):  # on
            self.write_cmd(cmd)

    def poweroff(self):
        self.write_cmd(_SET_DISP)

    def poweron(self):
        self.write_cmd(_SET_DISP | 0x01)

    def setContrast(self, contrast):
        self.write_cmd(_SET_CONTRAST)
        self.write_cmd(contrast)

    def invert(self, invert):
        self.write_cmd(_SET_NORM_INV | (invert & 1))

    def rotate(self, rotate):
        self.write_cmd(_SET_COM_OUT_DIR | ((rotate & 1) << 3))
        self.write_cmd(_SET_SEG_REMAP | (rotate & 1))

    def show(self):
        x0 = 0
        x1 = WIDTH - 1
        self.write_cmd(_SET_COL_ADDR)
        self.write_cmd(x0)
        self.write_cmd(x1)
        self.write_cmd(_SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)
        self.write_data(self.buffer)
        
    def write_cmd(self, cmd):
        try:
            self.i2c.writeto_mem(self.addr, int.from_bytes(b'\x80','big'), bytes([cmd]))
            self.comms_err = False
        except:
            print(i2c_err_str.format(self.addr))
            self.comms_err = True
            
    def write_data(self, buf):
        try:
            self.write_list[1] = buf
            self.i2c.writeto_mem(self.addr, int.from_bytes(self.write_list[0],'big'), self.write_list[1])
            self.comms_err = False
        except:
            print(i2c_err_str.format(self.addr))
            self.comms_err = True
            
    def circ(self,x,y,r,t=1,c=1):
        for i in range(x-r,x+r+1):
            for j in range(y-r,y+r+1):
                if t==1:
                    if((i-x)**2 + (j-y)**2 < r**2):
                        self.pixel(i,j,1)
                else:
                    if((i-x)**2 + (j-y)**2 < r**2) and ((i-x)**2 + (j-y)**2 >= (r-r*t-1)**2):
                        self.pixel(i,j,c)
                   
    def arc(self,x,y,r,stAng,enAng,t=0,c=1):
        for i in range(r*(1-t)-1,r):
            for ta in range(stAng,enAng,1):
                X = int(i*cos(radians(ta))+ x)
                Y = int(i*sin(radians(ta))+ y)
                self.pixel(X,Y,c)
            
    def load_pbm(self, filename, c):
        with open(filename, 'rb') as f:
            line = f.readline()
            if line.startswith(b'P4') is False:
                print('Not a valid pbm P4 file')
                return
            line = f.readline()
            while line.startswith(b'#') is True:
                line = f.readline()
            data_piicodev = bytearray(f.read())
        for byte in range(WIDTH // 8 * HEIGHT):
            for bit in range(8):
                if data_piicodev[byte] & 1 << bit != 0:
                    x_coordinate = ((7-bit) + (byte * 8)) % WIDTH
                    y_coordinate = byte * 8 // WIDTH
                    if x_coordinate < WIDTH and y_coordinate < HEIGHT:
                        self.pixel(x_coordinate, y_coordinate, c)
                        
    class graph2D:
        def __init__(self, originX = 0, originY = HEIGHT-1, width = WIDTH, height = HEIGHT, minValue=0, maxValue=255, c = 1, bars = False):
            self.minValue = minValue
            self.maxValue = maxValue
            self.originX = originX
            self.originY = originY
            self.width = width
            self.height = height
            self.c = c
            self.m = (1-height)/(maxValue-minValue)
            self.offset = originY-self.m*minValue
            self.bars = bars
            self.data = []

    def updateGraph2D(self, graph, value):
        graph.data.insert(0,value)
        if len(graph.data) > graph.width:
            graph.data.pop()
        x = graph.originX+graph.width-1
        m = graph.c
        for value in graph.data:
            y = round(graph.m*value + graph.offset)
            if graph.bars == True:
                for idx in range(y, graph.originY+1):
                    if x >= graph.originX and x < graph.originX+graph.width and idx <= graph.originY and idx > graph.originY-graph.height:
                        self.pixel(x,idx, m)
            else:
                if x >= graph.originX and x < graph.originX+graph.width and y <= graph.originY and y > graph.originY-graph.height:
                    self.pixel(x,y, m)
            x -= 1

class PiicoDev_SSD1306_MicroPython(PiicoDev_SSD1306):
    def __init__(self, bus=None, addr=0x3C):
        self.i2c = bus
        self.addr = addr
        self.temp = bytearray(2)
        self.write_list = [b'\x40', None]  # Co=0, D/C#=1
        self.init_display()
        super().__init__(self.buffer, WIDTH, HEIGHT, framebuf.MONO_VLSB)
        self.fill(0)
        self.show()
        
                       
def create_PiicoDev_SSD1306(address=0x3C,bus=None):
    display = PiicoDev_SSD1306_MicroPython(addr= address, bus=bus)
    return display
'''
# Test Code
from machine import SoftI2C, Pin
import fonts, time
import kooka
i2c = SoftI2C(scl=Pin('P3A'), sda=Pin('P3B'))
disp = create_PiicoDev_SSD1306(bus=i2c, address=0X3C)
x = 0
stages = ['Pixel test...','Geometry test...','Fonts Test']
stage = 0
while not kooka.button_a.was_pressed():
    disp.fill(0)
    disp.setfont(fonts.mono8x8)
    disp.text('Display Test',20,6)
    disp.setfont(fonts.mono6x7)
    disp.text('A-exit',6,60)
    disp.text(stages[stage], 0, 30)
    disp.show()
    time.sleep(1)
    if stage == 0:    # Pixel display test
        disp.fill(1)
        disp.show()
        stage += 1
        time.sleep(2)
        
    elif stage == 1:    # Geometry test 
        disp.fill(0)
        for x in range(0,128):    # draws a progressive diagonal line
            y = int(x/2)
            disp.line(0,0,x,y,1)
            disp.show()
        time.sleep(0.5)
        for x in range(0,64):    # draws progressively smaller rectangles
            disp.fill(0)
            y = int(x/2)
            disp.rect(x,y, 127-2*x, 63-2*y, 1)
            disp.show()
            time.sleep_ms(20)
        time.sleep(0.5)
        stage += 1

    elif stage == 2:    # Font test
        disp.fill(0)
        disp.pixel(0, 5, 1)
        disp.setfont(fonts.mono5x5)
        disp.text("5x5 Hello there Kookaberry!", 2, 5)

        disp.pixel(0, 13, 1)
        disp.setfont(fonts.mono6x7)
        disp.text("6x7 Hi Kookaberry!", 2, 13)

        disp.pixel(0, 23, 1)
        disp.setfont(fonts.mono8x8)
        disp.text("8x8 Kookaberry!", 2, 23)

        disp.pixel(0, 35, 1)
        disp.setfont(fonts.mono8x13)
        disp.text("8x13 Kookaberry!", 2, 35)

        disp.pixel(0, 56, 1)
        disp.setfont(fonts.sans12)
        disp.text("12 Kookaberry", 2, 56)
        
        disp.show()
        stage = 0
        time.sleep(1.5)
    else: pass
disp.fill(0)
disp.show()
'''