import machine, kooka
import time
from machine import Pin

temperature = None

def onewire_ds18_read_temp(p):
    import onewire, ds18x20
    ds = ds18x20.DS18X20(onewire.OneWire(Pin(p, Pin.PULL_UP)))
    roms = ds.scan()
    if not roms: return -100
    ds.convert_temp()
    time.sleep(0.75)
    return ds.read_temp(roms[0])



# Initialise timer counters.
_timer5000 = time.ticks_ms()

# Main loop code, run continuously.
while True:
    if time.ticks_diff(time.ticks_ms(), _timer5000) >= 0:
        _timer5000 += 5000
        kooka.display.clear()
        kooka.display.print('My Temperature', show=0)
        temperature = onewire_ds18_read_temp("P1")
        kooka.display.print('deg C', temperature, show=0)
        kooka.display.print('deg F', kooka.scale(temperature, from_=(0, 100), to=(32, 212)), show=0)
        kooka.display.show()
    kooka.display.show()
    machine.idle()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><variables><variable id="D0z,m%9V:Hv!%5LIXc%1">temperature</variable></variables><block type="event_every_seconds" id="`IQFR`23I}5hk4Mq,]?/" x="110" y="-50"><field name="T">5</field><statement name="DO"><block type="display_clear" id="GU6?a,gT+IJ5!uyfQx*+"><next><block type="display_print" id="!glngOu^kpfcIJ(.0IOo"><value name="VALUE"><shadow type="text" id="fU~[2AM:#+jYPLD2Ruwg"><field name="TEXT">My Temperature</field></shadow></value><next><block type="variables_set" id="NbPio#]Y){KM(s}gU+XT"><field name="VAR" id="D0z,m%9V:Hv!%5LIXc%1">temperature</field><value name="VALUE"><block type="onewire_ds18_read_temp_v2" id="TmV0ZVA7?|b-QOO[j2Cy"><value name="PIN"><block type="pin_selector_sensor" id="vpSOzO4S`CUy$1gsZ`=c"><field name="PIN">"P1"</field></block></value></block></value><next><block type="display_print2" id="r#b83xavIx_TN,waR7bl"><value name="VALUE1"><shadow type="text" id="HqvOGF4U+U}-Vn]1U~C|"><field name="TEXT">deg C</field></shadow></value><value name="VALUE2"><shadow type="math_number" id="L_C=I$nY!r)/SZm`!(fB"><field name="NUM">123</field></shadow><block type="variables_get" id="]kaVr:Ou!~gB7XJ2[Lsu"><field name="VAR" id="D0z,m%9V:Hv!%5LIXc%1">temperature</field></block></value><next><block type="display_print2" id="S}U:pB`=b95#)Ha~Uc_-"><value name="VALUE1"><shadow type="text" id="9G-8Mjpx#n-*Lisj)I?w"><field name="TEXT">deg F</field></shadow></value><value name="VALUE2"><shadow type="math_number" id="1|ed:/*Tm5akIgD~R`t-"><field name="NUM">123</field></shadow><block type="math_scale" id="@wxn9csOC{.o}C.)xn{E"><value name="VALUE"><shadow type="math_number" id="e_*lfaP7?PIG,I6-CTS!"><field name="NUM">0</field></shadow><block type="variables_get" id="Pax8TfHK+G+/LP9fS.^:"><field name="VAR" id="D0z,m%9V:Hv!%5LIXc%1">temperature</field></block></value><value name="FROM"><block type="tuple_range" id="J9v~r!Mho`Vy5!AhpaYz"><value name="MIN"><shadow type="math_number" id="v^C_G5apsk4,[b#t=A]y"><field name="NUM">0</field></shadow></value><value name="MAX"><shadow type="math_number" id="#N}G)LXy=s(v~80=r+)["><field name="NUM">100</field></shadow></value></block></value><value name="TO"><block type="tuple_range" id="WloLV{i[[;FBXk[p7u!H"><value name="MIN"><shadow type="math_number" id="pe1tH(Jpij,lSL.1@]|a"><field name="NUM">32</field></shadow></value><value name="MAX"><shadow type="math_number" id="N]/:E}vWw@`#Q.Y@uY#7"><field name="NUM">212</field></shadow></value></block></value></block></value><next><block type="display_show" id="C@jtcm:6z)[5%cx]5wB~"></block></next></block></next></block></next></block></next></block></next></block></statement></block></xml>
