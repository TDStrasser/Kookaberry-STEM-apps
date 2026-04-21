import machine, kooka
import time
from machine import Pin

def onewire_ds18_read_temp(p):
    import onewire, ds18x20
    ds = ds18x20.DS18X20(onewire.OneWire(Pin(p, Pin.PULL_UP)))
    roms = ds.scan()
    if not roms: return -100
    ds.convert_temp()
    time.sleep(0.75)
    return ds.read_temp(roms[0])


kooka.display.print('deg F', kooka.scale(onewire_ds18_read_temp("P1"), from_=(0, 100), to=(32, 212)), show=0)

kooka.display.show()

# Generated Blockly XML follows
# <xml xmlns="https://developers.google.com/blockly/xml"><block type="display_print2" id="?g#F1VeXfa?$%LYBtpTr" x="-110" y="-150"><value name="VALUE1"><shadow type="text" id="]DU#b_w0:`)ae.m8({1)"><field name="TEXT">deg F</field></shadow></value><value name="VALUE2"><shadow type="math_number" id="0|$tdYNB%^Z*tKw|Vh%("><field name="NUM">123</field></shadow><block type="math_scale" id="hPQ=o3S#AGN1sIenVI[g"><value name="VALUE"><shadow type="math_number" id="5fV%J-}tZ=v-r1^QfmZ{"><field name="NUM">0</field></shadow><block type="onewire_ds18_read_temp_v2" id="mLt4ZfBuD0g=CRi-d?O("><value name="PIN"><block type="pin_selector_sensor" id=";zZa|ei7xShn`XnkwghA"><field name="PIN">"P1"</field></block></value></block></value><value name="FROM"><block type="tuple_range" id="9tuh19($pR-]!_o3*0wb"><value name="MIN"><shadow type="math_number" id="Yr-uyqB|=Eb)$zBKxUue"><field name="NUM">0</field></shadow></value><value name="MAX"><shadow type="math_number" id="WyyNaW;AwMJyX+T4{J5h"><field name="NUM">100</field></shadow></value></block></value><value name="TO"><block type="tuple_range" id="+bAki0x}aL;lqQe{o?N+"><value name="MIN"><shadow type="math_number" id="b6;FMBFRTv98mFN!C:K["><field name="NUM">32</field></shadow></value><value name="MAX"><shadow type="math_number" id="dwodv4Xw|m|Sy7+JA+8|"><field name="NUM">212</field></shadow></value></block></value></block></value></block></xml>
