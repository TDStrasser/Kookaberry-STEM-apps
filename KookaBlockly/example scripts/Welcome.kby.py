import machine, kooka
import time



# Main loop code, run continuously.
while True:
    kooka.display.clear()
    kooka.display.print('Hello', show=0)
    kooka.display.show()
    time.sleep(1)
    kooka.display.print('Welcome to', show=0)
    kooka.display.print('the Kookaberry', show=0)
    kooka.display.show()
    for count in range(10):
        time.sleep(0.1)
        kooka.led_green.toggle()
        time.sleep(0.1)
        kooka.led_orange.toggle()
        time.sleep(0.1)
        kooka.led_red.toggle()
    kooka.display.print('Have fun!', show=0)
    kooka.display.show()
    time.sleep(2)
    kooka.display.show()
    machine.idle()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><block type="event_every_loop" id="B%Balaj:d;ga#HE,XEQ)" x="-50" y="-70"><statement name="DO"><block type="display_clear" id="?O}_Rsu-a~ETB`Kn{M6:"><next><block type="display_print" id="[~d){`i2-Whk6)Jo@RY="><value name="VALUE"><shadow type="text" id="9wH9+DPDWMlz[ga@lGxJ"><field name="TEXT">Hello</field></shadow></value><next><block type="display_show" id="Kz*FoFkWHSjmE0Z)UEf{"><next><block type="time_sleep" id="(ritV;t*5,%It:6bx|{A"><value name="VALUE"><shadow type="math_number" id="MFXG(L1.jejJb{~cLkd$"><field name="NUM">1</field></shadow></value><next><block type="display_print" id="TM8c8^BTIxWusn5g3u3A"><value name="VALUE"><shadow type="text" id="f6mM1Z|iDxYvVjZKIn[;"><field name="TEXT">Welcome to</field></shadow></value><next><block type="display_print" id=":3+S@r8J2R=T*=#%LXv^"><value name="VALUE"><shadow type="text" id="J*KJ9TBRz0{mV]0(m;K="><field name="TEXT">the Kookaberry</field></shadow></value><next><block type="display_show" id="$%=q9Mfyqj@KdH#ZI/uF"><next><block type="controls_repeat_ext" id="y|Zt%-]4Y]d7MGu,XC:L"><value name="TIMES"><block type="math_number" id=");;?j1oX/tux!]-`?P/%"><field name="NUM">10</field></block></value><statement name="DO"><block type="time_sleep" id="kmj8R8O=j8V7yy{n]!Zw"><value name="VALUE"><shadow type="math_number" id="w*!iz{!p~_Vro1A_jBge"><field name="NUM">0.1</field></shadow></value><next><block type="led_toggle" id="fp6]|.}+FY]V?%(;]kKX"><field name="LED">led_green</field><next><block type="time_sleep" id="5bI|#wWW}3v#hbMaz[9R"><value name="VALUE"><shadow type="math_number" id="_JQw)}TBKQ$(;rL*uRVO"><field name="NUM">0.1</field></shadow></value><next><block type="led_toggle" id="_%b}^zBMiu#dCG0C!)jh"><field name="LED">led_orange</field><next><block type="time_sleep" id="Y*Ko=2ocxqh:9Cr4%kyX"><value name="VALUE"><shadow type="math_number" id="6n7NE|%YCoxQ){*_q,UN"><field name="NUM">0.1</field></shadow></value><next><block type="led_toggle" id="~LMYJtPN0B:4f+C4k.eK"><field name="LED">led_red</field></block></next></block></next></block></next></block></next></block></next></block></statement><next><block type="display_print" id="%O?NS?u]O@z,hw*ZTWp4"><value name="VALUE"><shadow type="text" id="7J=GIU|FAK[j%@yDRP~6"><field name="TEXT">Have fun!</field></shadow></value><next><block type="display_show" id="L$S^3JaFHYUwAhElY^)="><next><block type="time_sleep" id="-}vnE~Wx$2T2AE^Z{a%n"><value name="VALUE"><shadow type="math_number" id="n*WN{W?Q0WNuN{/)g@Qj"><field name="NUM">2</field></shadow></value></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></statement></block></xml>
