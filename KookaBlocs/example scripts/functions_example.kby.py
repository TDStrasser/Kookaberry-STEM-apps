import machine, kooka
import time

# Describe this function...
def direction():
    if kooka.accel.get_xyz()[2] < 0:
        return 'up'
    return 'down'



# Initialise timer counters.
_timer1000 = time.ticks_ms()

# Main loop code, run continuously.
while True:
    if time.ticks_diff(time.ticks_ms(), _timer1000) >= 0:
        _timer1000 += 1000
        kooka.display.clear()
        kooka.display.print(direction(), show=0)
        kooka.display.show()
    kooka.display.show()
    machine.idle()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><block type="event_every_seconds" id="F:8~,sw/tKA6w7jS[5`r" x="130" y="-10"><field name="T">1</field><statement name="DO"><block type="display_clear" id=".l7Wgk0V[*8|%)#`|VBD"><next><block type="display_print" id="`2dy**taL?(_*|-MnXPd"><value name="VALUE"><shadow type="text" id="v16uoYY)dfFjyI*9,1pO"><field name="TEXT">Hello</field></shadow><block type="procedures_callreturn" id="JIj1!}SVa0,T]wQl~]q+"><mutation name="direction"></mutation></block></value><next><block type="display_show" id="Oj/Ul{P:T7NXIrMi9)S$"></block></next></block></next></block></statement></block><block type="procedures_defreturn" id="r3sRC/3zh1ErbsxC-HyH" x="130" y="130"><field name="NAME">direction</field><comment pinned="false" h="80" w="160">Describe this function...</comment><statement name="STACK"><block type="procedures_ifreturn" id="7R1i?PBK|jJ#s^1upCEN"><mutation value="1"></mutation><value name="CONDITION"><block type="logic_compare" id="GZ0rh*UUMC|FI?Lr`Ad6"><field name="OP">LT</field><value name="A"><block type="internal_accel_axis" id="!UP|sGtJ=X9M?.s$WA`P"><field name="AXIS">2</field></block></value><value name="B"><block type="math_number" id="Rfhz?xm*!W-5ncMwvFCS"><field name="NUM">0</field></block></value></block></value><value name="VALUE"><block type="text" id="iFr1acd/0!i#]|a;$o@`"><field name="TEXT">up</field></block></value></block></statement><value name="RETURN"><block type="text" id="0A.x)N3kx776|c8GNMh$"><field name="TEXT">down</field></block></value></block></xml>
