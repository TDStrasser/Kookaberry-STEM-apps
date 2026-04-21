import machine, kooka
import time
import fonts

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

# Main loop code, run continuously.
while True:
    if time.ticks_diff(time.ticks_ms(), _timer1000) >= 0:
        _timer1000 += 1000
        kooka.display.clear()
        kooka.display.setfont(fonts.mono6x7)
        kooka.display.print('Time:', datetime_format("{4:02}:{5:02}:{6:02}"), show=0)
    kooka.display.show()
    machine.idle()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><block type="event_every_seconds" id="H7JZHZf5jG,-;@}KnGqT" x="70" y="-10"><field name="T">1</field><statement name="DO"><block type="display_clear" id="F/8|7N}iObC.ZzSwQuj|"><next><block type="display_setfont" id="1$w8f(Sg4nZf|jz.!r6L"><field name="FONT">mono6x7</field><next><block type="display_print2" id="~j?Y(Q}u4RR86RnaY[MT"><value name="VALUE1"><shadow type="text" id="[/[gQj}R+}eD(bOk`Ie."><field name="TEXT">Time:</field></shadow></value><value name="VALUE2"><shadow type="math_number" id="ua==sgDLa9@?F]sPgl]A"><field name="NUM">123</field></shadow><block type="rtc_datetime1" id="b#L,s+_U/(9XwwVY_7!Q"><field name="DATETIME1">{4:02}:{5:02}:{6:02}</field></block></value></block></next></block></next></block></statement></block></xml>
