import kooka
from kooka.pn532 import PN532
from machine import SoftI2C
from time import sleep

# Define global objects.
i2c = SoftI2C(scl="P3A", sda="P3B")
rfid = PN532(i2c, address=36)
led_P1 = kooka.LED("P1")

# Main loop code.
while True:
    if rfid.tag_present():
        kooka.display.clear()
        kooka.display.show()
        led_P1.on()
        kooka.display.print('Tag:', rfid.read_type())
        sleep(2)
    else:
        kooka.display.clear()
        kooka.display.show()
        led_P1.off()
        kooka.display.print('Present Tag')

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><block type="rfid_config" id="Yne!Jt^tx,1W!U^9_7jp" x="310" y="30"><field name="VARIANT">PN532</field><value name="SCL"><block type="pin_selector_rfid" id="qjM:Frd#V=JCNRtlT|f{"><field name="PIN">"P3A"</field></block></value><value name="SDA"><block type="pin_selector_rfid" id="*qkKzH@9.7tT{}}sXlnk"><field name="PIN">"P3B"</field></block></value><value name="ADDR"><block type="math_number" id="bZ*{TkN7}U$~J-H0$m7%"><field name="NUM">36</field></block></value></block><block type="event_every_loop" id="%oT+3[_N$t0_{pv-v@%!" x="310" y="170"><statement name="DO"><block type="controls_if" id="B,(kJtx$cAXD/ZA(H;E-"><mutation else="1"></mutation><value name="IF0"><block type="rfid_tag_present" id="iF@%h3lIi!1,QZWX1:8O"></block></value><statement name="DO0"><block type="display_clear" id="v5[66h69Xk-l|sa7Hq/r"><next><block type="ext_led_on" id="YwsbzuU+LGmhs?t]I9g,"><value name="PIN"><block type="pin_selector_led" id="{u3M,/kG(hgmm7U7BR.;"><field name="PIN">"P1"</field></block></value><next><block type="display_print2" id="36Op!Q9bcb{TqKGP`gvx"><value name="VALUE1"><shadow type="text" id="w~f?pyV`pY_D5ofkE%lz"><field name="TEXT">Tag:</field></shadow></value><value name="VALUE2"><shadow type="math_number" id="8of0KE=^}O7aK9Z:}?i3"><field name="NUM">123</field></shadow><block type="rfid_read_info" id="CxTPD_}-DZpo#^GjFrtZ"><field name="PROPERTY">type</field></block></value><next><block type="time_sleep" id="iJ9}yzR|6Ju+XnqqzLMF"><value name="VALUE"><shadow type="math_number" id="Ic4H9:G}J!(=m8ikOS*t"><field name="NUM">2</field></shadow></value></block></next></block></next></block></next></block></statement><statement name="ELSE"><block type="display_clear" id="tTPs?5p,Khc5mQz(iTE3"><next><block type="ext_led_off" id="RMq0qIY_$xrS_29ElT,q"><value name="PIN"><block type="pin_selector_led" id="IDBh=~;qPwfae5hpT:A)"><field name="PIN">"P1"</field></block></value><next><block type="display_print" id="+Hyh4actuB#,*aW%t=6c"><value name="VALUE"><shadow type="text" id="WP/y)s~5$Ll?jRrwhu?3"><field name="TEXT">Present Tag</field></shadow></value></block></next></block></next></block></statement></block></statement></block></xml>
