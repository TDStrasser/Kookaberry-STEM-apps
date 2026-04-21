import machine, kooka
import fonts
import time

weekday_names = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
def datetime_format(*args, rtc=machine.RTC()):
    dt = rtc.datetime()
    s = ""
    for f in args:
        if f == "weekday":
            f = weekday_names[dt[3] - 1]
        else:
            f = f.format(*dt)
        s += f
    return s



# Initialise timer counters.
_timer1000 = time.ticks_ms()

# On-start code, run once at start-up.
if True:
    kooka.display.setfont(fonts.mono6x7)

# Main loop code, run continuously.
while True:
    if time.ticks_diff(time.ticks_ms(), _timer1000) >= 0:
        _timer1000 += 1000
        kooka.display.clear()
        kooka.display.print(datetime_format("{4:02}:{5:02}:{6:02}", "-", "{2:02}/{1:02}/{0}"), show=0)
    kooka.display.show()
    machine.idle()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><block type="event_on_start" id="m$#4m0r!Xh_AK,P4W9)E" x="110" y="-30"><statement name="DO"><block type="display_setfont" id="hwMYltLbDe9x-bkO?(jQ"><field name="FONT">mono6x7</field></block></statement></block><block type="event_every_seconds" id="w)dDemmelZAYh@kOQI*d" x="110" y="50"><field name="T">1</field><statement name="DO"><block type="display_clear" id="fsyoe=}N;`LO_9K8k`rl"><next><block type="display_print" id="w8:LaFmoloR=IwF9`{*P"><value name="VALUE"><shadow type="text" id="G;o]?Nk6iH47ZYtA)Yv)"><field name="TEXT">Hello</field></shadow><block type="rtc_datetime2" id="OEQ*9en,;Nb`xHx%Mn]^"><field name="DATETIME1">{4:02}:{5:02}:{6:02}</field><field name="SEP">-</field><field name="DATETIME2">{2:02}/{1:02}/{0}</field></block></value></block></next></block></statement></block></xml>
